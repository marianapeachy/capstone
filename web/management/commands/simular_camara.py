"""Simula una camara fija de sala que envia fotos a la app web (#58).

Registra la camara (CU05) y analiza, una por una, las fotos de una carpeta
tras degradarlas como lo hace una camara fija: poca resolucion, poca luz,
ruido del sensor y JPEG fuerte. Los resultados se ven en las paginas
Gondolas, Alertas y Analisis, como si los hubiera enviado la camara:

    python manage.py simular_camara data/raw/supermarket-shelves --pasillo 3 --gondola 14B --espera 10

Usar fotos que se pueden mostrar a terceros (Kaggle CC0, no SKU-110K).
"""

import time
from pathlib import Path

import cv2
import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError

from web.models import Camera
from web.views import analyze

EXTENSIONES = {".jpg", ".jpeg", ".png"}


def degradar(image: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Foto como la veria una camara de sala: 640 px de ancho, 70% de luz, ruido y JPEG de calidad 35."""
    alto, ancho = image.shape[:2]
    chica = cv2.resize(image, (640, round(alto * 640 / ancho)), interpolation=cv2.INTER_AREA)
    ruido = rng.normal(0, 8, chica.shape)
    return cv2.imdecode(cv2.imencode(".jpg", np.clip(chica * 0.7 + ruido, 0, 255).astype(np.uint8),
                                     [cv2.IMWRITE_JPEG_QUALITY, 35])[1], cv2.IMREAD_COLOR)


class Command(BaseCommand):
    help = "Simula una camara de sala: analiza fotos degradadas de una carpeta como si las enviara la camara."

    def add_arguments(self, parser):
        parser.add_argument("carpeta", help="carpeta con fotos .jpg o .png")
        parser.add_argument("--pasillo", required=True)
        parser.add_argument("--gondola", required=True)
        parser.add_argument("--nombre", default="Cámara de sala (simulada)")
        parser.add_argument("--espera", type=float, default=0, help="segundos entre fotos (0)")

    def handle(self, *args, carpeta, pasillo, gondola, nombre, espera, **options):
        fotos = sorted(p for p in Path(carpeta).glob("*") if p.suffix.lower() in EXTENSIONES)
        if not fotos:
            raise CommandError(f"No hay fotos .jpg o .png en {carpeta}.")
        Camera.objects.update_or_create(nombre=nombre, defaults={"pasillo": pasillo, "gondola": gondola})
        rng = np.random.default_rng(0)
        hechas = 0
        for i, foto in enumerate(fotos):
            image = cv2.imread(str(foto))
            if image is None:
                self.stderr.write(f"{foto.name}: no se pudo leer.")
                continue
            envio = SimpleUploadedFile(foto.stem + ".jpg", cv2.imencode(".jpg", degradar(image, rng))[1].tobytes())
            try:
                a = analyze(envio, None, pasillo, gondola)
            except ValueError as error:
                self.stderr.write(f"{foto.name}: {error}")
            else:
                hechas += 1
                self.stdout.write(f"{foto.name}: {a.free_fraction:.0%} libre{' - ALERTA' if a.critical else ''}")
            if espera and i < len(fotos) - 1:
                time.sleep(espera)
        self.stdout.write(f"{hechas} de {len(fotos)} fotos analizadas en {pasillo}/{gondola}.")
