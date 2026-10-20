"""Configuracion de Django. Lo que cambia entre el PC de desarrollo y el
servidor (CITT) llega por variables de entorno; ver "Aplicacion web" en el
README."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

ROOT = Path(__file__).resolve().parent.parent
# Base de datos y fotos analizadas (no versionadas; en Docker, un volumen).
DATA_DIR = Path(os.environ.get("SHELFVISION_DATA_DIR", ROOT / "data" / "processed" / "web"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
WEIGHTS = Path(os.environ.get(
    "SHELFVISION_WEIGHTS", ROOT / "data" / "processed" / "training" / "yolo26s" / "weights" / "best.pt"))

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or ("solo-desarrollo-no-usar-en-servidor" if DEBUG else "")
if not SECRET_KEY:
    raise ImproperlyConfigured("Sin DJANGO_DEBUG=1 hay que definir DJANGO_SECRET_KEY.")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "web",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "web.urls"
WSGI_APPLICATION = "web.wsgi.application"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "web.context.open_alerts",
    ]},
}]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": DATA_DIR / "db.sqlite3"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
MEDIA_ROOT = DATA_DIR / "media"
# Estilos, fuente e iconos salen de la app (web/static/), sin CDN: la red de la
# tienda o el servidor del CITT pueden no tener internet. whitenoise los sirve
# directo desde las carpetas de static, sin collectstatic.
STATIC_URL = "static/"
WHITENOISE_USE_FINDERS = True

AUTH_USER_MODEL = "web.User"
AUTHENTICATION_BACKENDS = ["web.auth.RutOrEmailBackend"]
# bcrypt, como promete la arquitectura de la Fase 1 (requiere el paquete bcrypt).
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "login"
# RNF04: la sesion expira tras 2 h sin uso (un turno no pide login a cada rato).
SESSION_COOKIE_AGE = 2 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True

# shortcut: los correos (enlace para definir la contrasena, CU06) se imprimen en
# la consola del servidor; para enviarlos de verdad, backend SMTP y EMAIL_HOST.
MAILERS = {"default": {"BACKEND": os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")}}
DEFAULT_FROM_EMAIL = "shelfvision@localhost"

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True
