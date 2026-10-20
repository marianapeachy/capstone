"""Punto de entrada WSGI (gunicorn en la imagen Docker)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
application = get_wsgi_application()

# RNF01: el modelo se carga al arrancar el servidor y no en la primera foto.
from web.views import get_detector  # noqa: E402

try:
    get_detector()
except FileNotFoundError:
    pass  # sin pesos la app parte igual; el analisis informa el error al subir una foto
