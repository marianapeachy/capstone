"""App web (item #28): login por perfil (CU00), usuarios y roles (CU06),
analisis de fotos (CU01), ciclo de las alertas (CU02), reportes (CU04, #7),
configuracion de umbral y camaras (CU05, #44) con la gondola
sintetica y el detector falso de pipeline_fixtures (sin pesos de YOLO26)."""

import json

import cv2
import numpy as np
import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from tests.pipeline_fixtures import ColorDetector, gondola
from web import forms, views
from web.auth import normalize_rut, valid_rut
from web.models import (ACTIVA, ADMIN, COMPLETADA, EN_PROCESO, JEFE, REEMPLAZADA, REPONEDOR, Analysis, Camera,
                        Config, User)

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


def test_si_falla_el_correo_el_usuario_queda_creado_y_se_reenvia_el_enlace(client, mailoutbox, monkeypatch):
    # #53: antes daba error 500 y el usuario quedaba sin contraseña ni forma de recibir el enlace.
    client.force_login(make_user("2-7", ADMIN))

    def fails(*args, **kwargs):
        raise OSError("servidor de correo caído")

    monkeypatch.setattr(views, "send_mail", fails)
    response = client.post(reverse("usuario_nuevo"), {
        "username": "12.345.678-5", "email": "ana@tienda.cl", "is_active": "on", "role": REPONEDOR}, follow=True)
    assert response.status_code == 200
    assert "no se pudo enviar el correo" in response.content.decode()
    user = User.objects.get(username="12345678-5")
    assert not user.has_usable_password()
    assert "Reenviar enlace" in client.get(reverse("usuario_editar", args=[user.pk])).content.decode()

    monkeypatch.undo()
    client.force_login(User.objects.get(username="2-7"))
    client.post(reverse("usuario_enlace", args=[user.pk]))
    assert len(mailoutbox) == 1 and mailoutbox[0].to == ["ana@tienda.cl"]


def test_solo_el_admin_reenvia_el_enlace(client, mailoutbox):
    user = make_user("1-9", REPONEDOR)
    client.force_login(make_user("2-7", JEFE))
    assert client.post(reverse("usuario_enlace", args=[user.pk])).status_code == 403
    assert not mailoutbox


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


def test_foto_sin_productos_se_rechaza_y_no_toca_la_alerta_abierta(client, analyzer):
    # #52: sin detecciones el cálculo daría 100% libre y una alerta falsa (foto tapada u oscura).
    client.force_login(make_user("1-9", JEFE))
    open_alert = analyzer(client)
    blank = SimpleUploadedFile("tapada.png", cv2.imencode(".png", np.full((600, 800, 3), 90, np.uint8))[1].tobytes(),
                               "image/png")
    response = client.post(reverse("analisis"), {"pasillo": "3", "gondola": "14B", "foto": blank})
    assert "No se detectaron productos" in response.content.decode()
    assert Analysis.objects.count() == 1
    open_alert.refresh_from_db()
    assert open_alert.estado == ACTIVA


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


# --- CU04 ---

def report(client, **params):
    today = timezone.localdate().isoformat()
    return client.get(reverse("reportes"), {"desde": today, "hasta": today, "formato": "csv", **params})


def test_reporte_csv_trae_una_fila_por_analisis_con_libre_y_alerta(client, analyzer):
    client.force_login(make_user("1-9", JEFE))
    analyzer(client)  # con quiebre
    analyzer(client, empty=None, gondola_id="15")  # góndola llena, sin quiebre
    response = report(client)
    assert response["Content-Disposition"].startswith("attachment")
    header, first, second = response.content.decode("utf-8-sig").splitlines()
    assert header == "Fecha,Pasillo,Góndola,% libre,Alerta,Estado,Subida por"
    assert ",3,14B," in first and ",Sí,Activa," in first
    assert ",3,15," in second and ",No,Sin quiebre," in second


def test_reporte_filtra_por_gondola(client, analyzer):
    client.force_login(make_user("1-9", JEFE))
    analyzer(client)
    analyzer(client, empty=None, gondola_id="15")
    lines = report(client, gondola="15").content.decode("utf-8-sig").splitlines()
    assert len(lines) == 2 and ",15," in lines[1]


@pytest.mark.parametrize("formato, tipo", [("xlsx", "spreadsheetml"), ("pdf", "application/pdf")])
def test_reporte_excel_y_pdf(client, analyzer, formato, tipo):
    client.force_login(make_user("1-9", ADMIN))
    analyzer(client)
    response = report(client, formato=formato)
    assert tipo in response["Content-Type"]
    assert response["Content-Disposition"].endswith(f'.{formato}"')


def test_reporte_sin_datos_avisa_y_no_genera_archivo(client):
    client.force_login(make_user("1-9", JEFE))
    response = report(client, desde="2020-01-01", hasta="2020-01-31")
    assert "Content-Disposition" not in response
    assert "No hay análisis" in response.content.decode()


def test_reporte_rechaza_periodo_invertido(client):
    client.force_login(make_user("1-9", JEFE))
    response = report(client, desde="2026-10-21", hasta="2026-10-01")
    assert "Content-Disposition" not in response
    assert response.context["form"].errors


def test_reponedor_no_exporta_reportes(client):
    client.force_login(make_user("1-9", REPONEDOR))
    assert client.get(reverse("reportes")).status_code == 403


# --- CU05 ---

CALIBRATION = {"camera_matrix": [[800, 0, 399.5], [0, 800, 299.5], [0, 0, 1]],
               "dist_coeffs": [-0.1, 0, 0, 0], "fisheye": False}


def calibration_file(data):
    return SimpleUploadedFile("calibracion.json", json.dumps(data).encode(), "application/json")


def test_admin_cambia_el_umbral_y_rige_para_las_fotos_siguientes(client, analyzer):
    client.force_login(make_user("2-7", ADMIN))
    before = analyzer(client)  # 36% libre: con el umbral de 30% por defecto, alerta
    response = client.post(reverse("configuracion"), {"umbral": 40}, follow=True)
    assert "Parámetros actualizados" in response.content.decode()
    after = analyzer(client, gondola_id="15")
    before.refresh_from_db()
    assert before.critical and not after.critical  # lo ya analizado no cambia
    assert "al menos 40%" in client.get(reverse("alertas")).content.decode()


@pytest.mark.parametrize("umbral", [0, 101, ""])
def test_umbral_fuera_de_rango_se_rechaza_y_queda_el_anterior(client, umbral):
    client.force_login(make_user("2-7", ADMIN))
    response = client.post(reverse("configuracion"), {"umbral": umbral})
    assert "Umbral inválido" in response.content.decode()
    assert Config.get().umbral == 30


def test_la_calibracion_de_la_camara_se_usa_al_analizar_su_gondola(client, analyzer, monkeypatch):
    client.force_login(make_user("2-7", ADMIN))
    client.post(reverse("camara_nueva"), {
        "nombre": "Cámara 1", "pasillo": "3", "gondola": "14B", "calibracion": calibration_file(CALIBRATION)})
    seen = []
    real = views.run_image
    monkeypatch.setattr(views, "run_image", lambda image, detector, **kw: seen.append(kw) or real(image, detector, **kw))
    analyzer(client)  # pasillo 3, góndola 14B: tiene cámara
    analyzer(client, gondola_id="15")  # sin cámara: solo CLAHE
    assert seen[0]["calibration"].dist_coeffs[0] == -0.1
    assert seen[1]["calibration"] is None


def test_editar_camara_sin_archivo_conserva_la_calibracion(client):
    client.force_login(make_user("2-7", ADMIN))
    client.post(reverse("camara_nueva"), {
        "nombre": "Cámara 1", "pasillo": "3", "gondola": "14B", "calibracion": calibration_file(CALIBRATION)})
    camera = Camera.objects.get()
    client.post(reverse("camara_editar", args=[camera.pk]), {"nombre": "Cámara 1", "pasillo": "4", "gondola": "14B"})
    camera.refresh_from_db()
    assert camera.pasillo == "4" and camera.calibracion == CALIBRATION


@pytest.mark.parametrize("data", [
    {"camera_matrix": [[1, 0], [0, 1]], "dist_coeffs": [0, 0, 0, 0]},  # matriz que no es 3x3
    {"camera_matrix": CALIBRATION["camera_matrix"]},  # faltan los coeficientes
])
def test_calibracion_invalida_se_rechaza(client, data):
    client.force_login(make_user("2-7", ADMIN))
    response = client.post(reverse("camara_nueva"), {
        "nombre": "Cámara 1", "pasillo": "3", "gondola": "14B", "calibracion": calibration_file(data)})
    assert "Calibración inválida" in response.content.decode()
    assert not Camera.objects.exists()


def test_una_gondola_tiene_una_sola_camara(client):
    client.force_login(make_user("2-7", ADMIN))
    client.post(reverse("camara_nueva"), {"nombre": "Cámara 1", "pasillo": "3", "gondola": "14B"})
    response = client.post(reverse("camara_nueva"), {"nombre": "Cámara 2", "pasillo": "3", "gondola": "14B"})
    assert response.context["form"].errors
    assert Camera.objects.count() == 1


def test_solo_el_admin_configura(client):
    client.force_login(make_user("1-9", JEFE))
    assert client.get(reverse("configuracion")).status_code == 403
    assert client.get(reverse("camara_nueva")).status_code == 403
