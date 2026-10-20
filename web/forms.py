from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group

from web.auth import normalize_rut, valid_rut
from web.models import ADMIN, ROLES, User

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
