"""Settings de pytest: los tests no usan HTTPS ni exigen una clave real."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "solo-tests")
os.environ["DJANGO_HTTPS"] = "0"

from web.settings import *  # noqa: E402,F401,F403
