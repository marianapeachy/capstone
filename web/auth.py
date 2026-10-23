"""Login de CU00: con RUT o correo. Tras 5 intentos fallidos seguidos la
cuenta se bloquea 15 minutos y se desbloquea sola (#51): desactivarla dejaba
que cualquiera que supiera un RUT sacara a otro, incluso al unico
Administrador. El Administrador la desbloquea antes al guardarla en CU06."""

import itertools
import re
from datetime import timedelta

from django.contrib.auth import get_user_model, user_logged_in, user_login_failed
from django.contrib.auth.backends import ModelBackend
from django.db.models import F
from django.dispatch import receiver
from django.utils import timezone

MAX_FAILED_LOGINS = 5
LOCK_TIME = timedelta(minutes=15)
RUT_PATTERN = re.compile(r"^[\d.\s]+-[\dkK]$")


def normalize_rut(rut: str) -> str:
    """12.345.678-k -> 12345678-K; lo que no parece RUT queda igual."""
    rut = rut.strip()
    return re.sub(r"[.\s]", "", rut).upper() if RUT_PATTERN.match(rut) else rut


def valid_rut(rut: str) -> bool:
    """Digito verificador por modulo 11 (RUT ya normalizado)."""
    body, _, dv = rut.rpartition("-")
    if not body.isdigit():
        return False
    total = sum(int(d) * f for d, f in zip(reversed(body), itertools.cycle(range(2, 8))))
    rest = 11 - total % 11
    return dv == {10: "K", 11: "0"}.get(rest, str(rest))


def find_user(login: str):
    users = get_user_model().objects
    if "@" in login:
        return users.filter(email__iexact=login.strip()).first()
    return users.filter(username=normalize_rut(login)).first()


def locked(user) -> bool:
    return bool(user.locked_until and user.locked_until > timezone.now())


class RutOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = find_user(username or "")
        return super().authenticate(request, user.username if user else username, password, **kwargs)

    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and not locked(user)


@receiver(user_login_failed)
def count_failure(sender, credentials, **kwargs):
    user = find_user(credentials.get("username") or "")
    if not user or not user.is_active or locked(user):  # bloqueada: los intentos no alargan el bloqueo
        return
    # La suma va en la base (F): intentos en paralelo no se pierden ni pasan de 5 sin bloquear.
    row = get_user_model().objects.filter(pk=user.pk)
    row.update(failed_logins=F("failed_logins") + 1)
    row.filter(failed_logins__gte=MAX_FAILED_LOGINS).update(failed_logins=0, locked_until=timezone.now() + LOCK_TIME)


@receiver(user_logged_in)
def reset_failures(sender, user, **kwargs):
    if user.failed_logins:
        user.failed_logins = 0
        user.save(update_fields=["failed_logins"])
