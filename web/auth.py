"""Login de CU00: con RUT o correo, y la cuenta se bloquea (inactiva) tras 5
intentos fallidos seguidos; el Administrador la reactiva en CU06."""

import itertools
import re

from django.contrib.auth import get_user_model, user_logged_in, user_login_failed
from django.contrib.auth.backends import ModelBackend
from django.dispatch import receiver

MAX_FAILED_LOGINS = 5
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


class RutOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = find_user(username or "")
        return super().authenticate(request, user.username if user else username, password, **kwargs)


@receiver(user_login_failed)
def count_failure(sender, credentials, **kwargs):
    user = find_user(credentials.get("username") or "")
    if user and user.is_active:
        user.failed_logins += 1
        user.is_active = user.failed_logins < MAX_FAILED_LOGINS
        user.save(update_fields=["failed_logins", "is_active"])


@receiver(user_logged_in)
def reset_failures(sender, user, **kwargs):
    if user.failed_logins:
        user.failed_logins = 0
        user.save(update_fields=["failed_logins"])
