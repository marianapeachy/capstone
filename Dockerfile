# Python 3.13: 3.10 termina su soporte en octubre de 2026 y Django 6.1 (app
# web) exige 3.12 o superior.
FROM python:3.13-slim-trixie

# Librerias de sistema que necesita opencv-python (lo exige ultralytics; ver
# requirements.txt). Nombres de paquete de Debian 13 (trixie): la base se fija
# a trixie porque en otras versiones de Debian cambian (ej. libglib2.0-0t64).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0t64 \
    libsm6 \
    libice6 \
    libxext6 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# PyTorch solo CPU: desde PyPI, pip instala en Linux la variante CUDA
# (~0.5 GB de torch mas varios GB de toolkit CUDA/cuDNN) aunque no haya GPU.
# Se actualiza pip antes: el 23.0.1 de la imagen base rechaza wheels del
# indice de PyTorch (ej. typing_extensions) por la normalizacion del nombre
# e intenta compilarlos desde fuente, sin las dependencias de build.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY web/ ./web/
COPY manage.py pytest.ini ./

# App web (item #28). /data es el volumen con la base de datos, las fotos
# analizadas y los pesos (best.pt): sin volumen se pierden al recrear el
# contenedor. DJANGO_SECRET_KEY y DJANGO_ALLOWED_HOSTS se pasan con -e.
# El pipeline por lotes sigue disponible: docker run ... python scripts/run_pipeline.py
ENV DJANGO_DEBUG=0 \
    SHELFVISION_DATA_DIR=/data \
    SHELFVISION_WEIGHTS=/data/best.pt
EXPOSE 8000
# Un solo worker: cada uno cargaria su propia copia de YOLO26 en memoria.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn web.wsgi --bind 0.0.0.0:8000 --workers 1 --threads 4 --timeout 120"]
