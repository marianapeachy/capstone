import json

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group

from src.pipeline import LensCalibration
from web.auth import normalize_rut, valid_rut
from web.models import ADMIN, ROLES, Camera, Config, User

MAX_PHOTO_MB = 20


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="RUT o correo", max_length=254)
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Credenciales incorrectas. Intente nuevamente.",
    }


class UserForm(forms.ModelForm):
    """CU06: datos del usuario, rol y estado (Activo/Inactivo)."""

    role = forms.ChoiceField(label="Rol", choices=[(r, r) for r in ROLES])

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]
        labels = {"username": "RUT", "is_active": "Cuenta activa"}
        help_texts = {"username": "Con guion y dígito verificador, por ejemplo 12.345.678-5.",
                      "is_active": "Desmarcar para desactivar la cuenta (baja de personal)."}

    def __init__(self, *args, editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.editor = editor
        if self.instance.pk:
            self.initial["role"] = self.instance.role

    def clean_username(self):
        rut = normalize_rut(self.cleaned_data["username"])
        if not valid_rut(rut):
            raise forms.ValidationError("RUT inválido: revise el dígito verificador.")
        return rut

    def clean(self):
        data = super().clean()
        # Un Administrador no puede dejarse fuera a sí mismo.
        if self.editor and self.instance.pk == self.editor.pk and (
                not data.get("is_active") or data.get("role") != ADMIN):
            raise forms.ValidationError("No puede desactivar su propia cuenta ni quitarse el rol de Administrador.")
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        if user._state.adding:
            user.set_unusable_password()  # la define el usuario con el enlace del correo
        if user.is_active:
            user.failed_logins = 0  # reactivar desbloquea una cuenta bloqueada por intentos
        user.save()
        user.groups.set([Group.objects.get(name=self.cleaned_data["role"])])
        return user


class PhotoForm(forms.Form):
    pasillo = forms.CharField(label="Pasillo", max_length=20)
    gondola = forms.CharField(label="Góndola", max_length=20)
    foto = forms.ImageField(label="Foto de la góndola", help_text=f"JPG o PNG, hasta {MAX_PHOTO_MB} MB.",
                            widget=forms.FileInput(attrs={"accept": "image/jpeg,image/png"}))

    def clean_foto(self):
        foto = self.cleaned_data["foto"]
        if foto.size > MAX_PHOTO_MB * 1024 * 1024:
            raise forms.ValidationError(f"La foto pesa más de {MAX_PHOTO_MB} MB.")
        return foto


class ReportForm(forms.Form):
    """CU04: periodo, ubicacion opcional y formato del reporte."""

    desde = forms.DateField(label="Desde", widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    hasta = forms.DateField(label="Hasta", widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    pasillo = forms.CharField(label="Pasillo", max_length=20, required=False,
                              widget=forms.TextInput(attrs={"placeholder": "Todos"}))
    gondola = forms.CharField(label="Góndola", max_length=20, required=False,
                              widget=forms.TextInput(attrs={"placeholder": "Todas"}))
    formato = forms.ChoiceField(label="Formato", choices=[("xlsx", "Excel (.xlsx)"), ("csv", "CSV"), ("pdf", "PDF")])

    def clean(self):
        data = super().clean()
        if data.get("desde") and data.get("hasta") and data["desde"] > data["hasta"]:
            raise forms.ValidationError("La fecha «Desde» no puede ser posterior a «Hasta».")
        return data


class ConfigForm(forms.ModelForm):
    """CU05: umbral de espacio libre desde el que se alerta (1% a 100%)."""

    class Meta:
        model = Config
        fields = ["umbral"]
        help_texts = {"umbral": "Se alerta cuando el espacio libre de la góndola llega a este porcentaje del frente. "
                                "Rige para las fotos siguientes."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        invalid = "Umbral inválido: debe ser un número entero entre 1 y 100."
        self.fields["umbral"].error_messages.update(required=invalid, invalid=invalid, min_value=invalid,
                                                    max_value=invalid)
        self.fields["umbral"].widget.attrs.update(min=1, max=100)


class CameraForm(forms.ModelForm):
    """CU05: camara asociada a un pasillo y una gondola, con su calibracion
    de lente opcional (JSON de OpenCV). Sin archivo nuevo se conserva la
    calibracion que ya tenia."""

    calibracion = forms.FileField(
        label="Calibración de lente (opcional)", required=False,
        help_text='Archivo JSON con "camera_matrix" (3x3), "dist_coeffs" y "fisheye" (true o false), '
                  "como lo entrega la calibración de OpenCV. Sin calibración solo se corrige el contraste.",
        widget=forms.FileInput(attrs={"accept": "application/json,.json"}))

    class Meta:
        model = Camera
        fields = ["nombre", "pasillo", "gondola"]

    def clean_calibracion(self):
        upload = self.cleaned_data["calibracion"]
        if not upload:
            return None
        if upload.size > 100_000:  # una calibracion ocupa unos cientos de bytes
            raise forms.ValidationError("Calibración inválida: el archivo es demasiado grande.")
        try:
            data = json.loads(upload.read().decode("utf-8"))
            calibration = LensCalibration(camera_matrix=data["camera_matrix"], dist_coeffs=data["dist_coeffs"],
                                          fisheye=bool(data.get("fisheye", False)))
        except KeyError as error:
            raise forms.ValidationError(f"Calibración inválida: falta el campo {error}.") from error
        except (ValueError, TypeError) as error:  # JSON mal formado o matrices con forma incorrecta
            raise forms.ValidationError(f"Calibración inválida: {error}") from error
        return {"camera_matrix": calibration.camera_matrix.tolist(), "dist_coeffs": calibration.dist_coeffs.tolist(),
                "fisheye": calibration.fisheye}

    def save(self, commit=True):
        camera = super().save(commit=False)
        if self.cleaned_data["calibracion"] is not None:
            camera.calibracion = self.cleaned_data["calibracion"]
        if commit:
            camera.save()
        return camera
