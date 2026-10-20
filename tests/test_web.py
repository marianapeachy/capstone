"""App web (item #28): login por perfil (CU00), usuarios y roles (CU06),
analisis de fotos (CU01) y ciclo de las alertas (CU02), con la gondola
sintetica y el detector falso de pipeline_fixtures (sin pesos de YOLO26)."""

import cv2
import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from tests.pipeline_fixtures import ColorDetector, gondola
from web import forms, views
from web.auth import normalize_rut, valid_rut
from web.models import ACTIVA, ADMIN, COMPLETADA, EN_PROCESO, JEFE, REEMPLAZADA, REPONEDOR, Analysis, User

pytestmark = pytest.mark.django_db
PASSWORD = "clave-de-prueba-123"
EMPTIED = {1: (0.15, 0.85), 2: (0.15, 0.85)}


def make_user(rut, role):
    user = User.objects.create_user(normalize_rut(rut), email=f"{normalize_rut(rut)}@tienda.cl", password=PASSWORD)
    user.groups.add(Group.objects.get(name=role))
    return user


def login(client, username, password=PASSWORD):
    return client.post(reverse("login"), {"username": username, "password": password})


def photo(empty=None, name="gondola.png"):
    image, _ = gondola(empty)
    return SimpleUploadedFile(name, cv2.imencode(".png", image)[1].tobytes(), "image/png")


@pytest.fixture
def analyzer(settings, tmp_path, monkeypatch):
    """Sube fotos con el detector falso y devuelve el analisis creado."""
    settings.MEDIA_ROOT = tmp_path
    monkeypatch.setattr(views, "get_detector", ColorDetector)

    def upload(client, empty=EMPTIED, pasillo="3", gondola_id="14B"):
        client.post(reverse("analisis"), {"pasillo": pasillo, "gondola": gondola_id, "foto": photo(empty)})
        return Analysis.objects.first()

    return upload


# --- CU00 ---

@pytest.mark.parametrize("role, home", [(ADMIN, "usuarios"), (JEFE, "analisis"), (REPONEDOR, "alertas")])
def test_login_lleva_a_la_vista_de_su_perfil(client, role, home):
    make_user("11111111-1", role)
    login(client, "11.111.111-1")  # con puntos: se normaliza
    assert client.get(reverse("inicio")).url == reverse(home)


def test_login_con_correo(client):
    make_user("1-9", JEFE)
    assert login(client, "1-9@tienda.cl").url == reverse("inicio")


def test_bloquea_tras_5_intentos_y_el_admin_la_reactiva(client):
    user = make_user("1-9", JEFE)
    for _ in range(5):
        response = login(client, "1-9", "mala")
    assert "Credenciales incorrectas" in response.content.decode()
    user.refresh_from_db()
    assert not user.is_active
    assert login(client, "1-9").status_code == 200  # sigue bloqueada con la clave buena

    client.force_login(make_user("2-7", ADMIN))
    client.post(reverse("usuario_editar", args=[user.pk]), {
        "username": "1-9", "email": user.email, "is_active": "on", "role": JEFE})
    user.refresh_from_db()
    assert user.is_active and user.failed_logins == 0


def test_desactivar_cierra_la_sesion_abierta(client):
    user = make_user("1-9", JEFE)
    client.force_login(user)
    user.is_active = False
    user.save()
    assert client.get(reverse("analisis")).url.startswith(reverse("login"))


def test_cada_perfil_ve_solo_lo_suyo(client):
    client.force_login(make_user("1-9", REPONEDOR))
    assert client.get(reverse("usuarios")).status_code == 403
    assert client.get(reverse("analisis")).status_code == 403
    assert client.get(reverse("alertas")).status_code == 200


# --- CU06 ---

def test_admin_crea_usuario_que_define_su_clave_con_enlace_de_un_uso(client, mailoutbox):
    client.force_login(make_user("2-7", ADMIN))
    client.post(reverse("usuario_nuevo"), {
        "username": "12.345.678-5", "first_name": "Ana", "email": "ana@tienda.cl", "is_active": "on",
        "role": REPONEDOR})
    user = User.objects.get(username="12345678-5")
    assert user.role == REPONEDOR and not user.has_usable_password()

    link = mailoutbox[0].body.split()[-1]
    client.logout()
    form_url = client.get(link, follow=True).redirect_chain[-1][0]
    new = "otra-clave-segura-9"
    client.post(form_url, {"new_password1": new, "new_password2": new})
    assert client.login(username="12345678-5", password=new)
    assert not client.get(link, follow=True).context["validlink"]


@pytest.mark.parametrize("rut, valid", [
    ("12345678-5", True), ("11111111-1", True), ("1-9", True), ("12345678-6", False), ("abc-1", False)])
def test_digito_verificador_del_rut(rut, valid):
    assert valid_rut(rut) is valid


def test_rut_con_digito_malo_no_crea_cuenta(client):
    client.force_login(make_user("2-7", ADMIN))
    response = client.post(reverse("usuario_nuevo"), {
        "username": "12.345.678-6", "email": "x@tienda.cl", "is_active": "on", "role": JEFE})
    assert "RUT inválido" in response.content.decode()
    assert not User.objects.filter(email="x@tienda.cl").exists()


def test_admin_no_puede_desactivarse_a_si_mismo(client):
    admin = make_user("2-7", ADMIN)
    client.force_login(admin)
    client.post(reverse("usuario_editar", args=[admin.pk]), {
        "username": "2-7", "email": admin.email, "role": ADMIN})  # sin is_active
    admin.refresh_from_db()
    assert admin.is_active


# --- CU01 y CU02 ---

def test_analisis_de_foto_abre_alerta_con_ubicacion_y_franjas(client, analyzer):
    client.force_login(make_user("1-9", JEFE))
    analysis = analyzer(client)
    assert analysis.critical and analysis.free_fraction >= 0.3 and analysis.estado == ACTIVA
    assert analysis.location == "Pasillo 3 · Góndola 14B"
    assert any(strip["gaps"] for strip in analysis.strips)
    assert client.get(reverse("alertas")).context["alertas"] == [analysis]
    assert client.get(reverse("analisis_imagen", args=[analysis.pk]))["Content-Type"] == "image/jpeg"


def test_reponedor_toma_y_completa_la_alerta(client, analyzer):
    client.force_login(make_user("1-9", JEFE))
    analysis = analyzer(client)
    reponedor = make_user("2-7", REPONEDOR)
    client.force_login(reponedor)

    client.post(reverse("alerta_accion", args=[analysis.pk, "tomar"]))
    analysis.refresh_from_db()
    assert analysis.estado == EN_PROCESO and analysis.taken_by == reponedor

    client.post(reverse("alerta_accion", args=[analysis.pk, "completar"]))
    analysis.refresh_from_db()
    assert analysis.estado == COMPLETADA
    assert client.get(reverse("alertas")).context["alertas"] == []


def test_foto_nueva_reemplaza_la_alerta_o_confirma_la_reposicion(client, analyzer):
    client.force_login(make_user("1-9", JEFE))
    first = analyzer(client)
    second = analyzer(client)  # sigue en quiebre: una sola alerta abierta
    first.refresh_from_db()
    assert first.estado == REEMPLAZADA and second.estado == ACTIVA

    analyzer(client, empty={})  # góndola llena: confirma la reposición
    second.refresh_from_db()
    assert second.estado == COMPLETADA
    assert not Analysis.objects.filter(estado__in=[ACTIVA, EN_PROCESO]).exists()


def test_foto_demasiado_grande_se_rechaza(client, analyzer, monkeypatch):
    client.force_login(make_user("1-9", JEFE))
    monkeypatch.setattr(forms, "MAX_PHOTO_MB", 0)  # cualquier foto supera el límite
    response = client.post(reverse("analisis"), {"pasillo": "3", "gondola": "1", "foto": photo()})
    assert "pesa más de" in response.content.decode()
    assert not Analysis.objects.exists()


def test_archivo_que_no_es_imagen_se_rechaza(client):
    client.force_login(make_user("1-9", JEFE))
    fake = SimpleUploadedFile("foto.jpg", b"no soy una imagen", "image/jpeg")
    response = client.post(reverse("analisis"), {"pasillo": "3", "gondola": "1", "foto": fake})
    assert response.context["form"].errors
    assert not Analysis.objects.exists()


def test_estados_vacios(client):
    client.force_login(make_user("1-9", JEFE))
    assert "Sin quiebres abiertos" in client.get(reverse("alertas")).content.decode()
    assert "Todavía no hay análisis" in client.get(reverse("analisis")).content.decode()


def test_no_informa_porcentaje_ni_quiebre_por_repisa(client, analyzer):
    # Alcance del 2026-10-19 (#40): solo se informan el % libre y la alerta de la góndola completa.
    client.force_login(make_user("1-9", JEFE))
    analysis = analyzer(client)
    assert all(set(strip) == {"number", "gaps"} for strip in analysis.strips)
    for url in (reverse("alertas"), reverse("analisis_detalle", args=[analysis.pk])):
        page = client.get(url).content.decode()
        assert "shelf-free" not in page and "Quiebre en repisa" not in page
