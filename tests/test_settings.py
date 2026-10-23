"""Configuracion segura por defecto de la app web (item #50)."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOW = ("import web.settings as s; "
        "print(s.DEBUG, s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE, s.SECURE_SSL_REDIRECT)")


def settings_with(**env):
    base = {k: v for k, v in os.environ.items() if not k.startswith("DJANGO_")}
    return subprocess.run([sys.executable, "-c", SHOW], cwd=ROOT, env={**base, **env},
                          capture_output=True, text=True)


def test_debug_is_off_by_default_and_needs_a_secret_key():
    result = settings_with()
    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY" in result.stderr


def test_https_is_on_by_default_without_debug():
    result = settings_with(DJANGO_SECRET_KEY="x")
    assert result.stdout.split() == ["False", "True", "True", "True"]


def test_https_can_be_turned_off_for_a_server_without_tls():
    result = settings_with(DJANGO_SECRET_KEY="x", DJANGO_HTTPS="0")
    assert result.stdout.split() == ["False", "False", "False", "False"]


def test_debug_keeps_cookies_and_redirect_off():
    result = settings_with(DJANGO_DEBUG="1")
    assert result.stdout.split() == ["True", "False", "False", "False"]
