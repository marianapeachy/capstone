FROM python:3.10-slim-trixie

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

CMD ["python", "scripts/run_pipeline.py"]
