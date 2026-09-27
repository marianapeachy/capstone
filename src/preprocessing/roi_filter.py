"""Recorte de la region de interes (ROI) sobre la gondola detectada.

Parte del enfoque hibrido (ver CLAUDE.md): antes de la inferencia YOLO26
se recorta la imagen a la gondola para descartar pasillo, techo y piso.
La ROI la entrega la segmentacion automatica de la gondola (ningun
usuario la configura); este modulo solo la normaliza y recorta.
Toda ROI entra y sale en el formato
estandar del proyecto: [x_min, y_min, x_max, y_max] en pixeles absolutos
de la imagen original.

Las imagenes son arrays de NumPy tal como los entrega OpenCV
(cv2.imread): (alto, ancho) en escala de grises o (alto, ancho, canales)
en BGR.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from src.preprocessing._validation import check_image

BBox = tuple[float, float, float, float]
PixelBBox = tuple[int, int, int, int]


@dataclass(frozen=True)
class RoiCrop:
    """Imagen recortada junto con la ROI (en coordenadas de la imagen
    original) de la que proviene, para poder volver a ese sistema de
    coordenadas despues de la inferencia."""

    image: np.ndarray
    roi: PixelBBox

    def to_original(self, bbox: BBox) -> BBox:
        """Traslada un bbox expresado en coordenadas del recorte (ej. una
        deteccion de YOLO26) a coordenadas absolutas de la imagen
        original, que es el estandar del proyecto."""
        x_min, y_min, x_max, y_max = bbox
        offset_x, offset_y = self.roi[0], self.roi[1]
        return (
            x_min + offset_x,
            y_min + offset_y,
            x_max + offset_x,
            y_max + offset_y,
        )


def normalize_roi(roi: BBox, width: int, height: int) -> PixelBBox:
    """Normaliza una ROI al estandar del proyecto dentro de una imagen de
    `width` x `height`: ordena min/max, redondea hacia afuera a pixeles
    enteros (floor en el minimo, ceil en el maximo, para no perder el
    borde de un bbox con decimales) y recorta a los limites de la imagen.

    Lanza ValueError si la ROI tiene coordenadas no finitas o si no se
    intersecta con la imagen (area nula tras el recorte).
    """
    if len(roi) != 4:
        raise ValueError(f"La ROI debe tener 4 coordenadas, se recibio {roi!r}")
    if not all(math.isfinite(c) for c in roi):
        raise ValueError(f"La ROI contiene coordenadas no finitas: {roi!r}")

    x_min, y_min, x_max, y_max = roi
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min

    x_min_px = max(0, min(math.floor(x_min), width))
    y_min_px = max(0, min(math.floor(y_min), height))
    x_max_px = max(0, min(math.ceil(x_max), width))
    y_max_px = max(0, min(math.ceil(y_max), height))

    if x_max_px <= x_min_px or y_max_px <= y_min_px:
        raise ValueError(
            f"La ROI {roi!r} queda fuera de la imagen de {width}x{height} px"
        )
    return x_min_px, y_min_px, x_max_px, y_max_px


def crop_roi(image: np.ndarray | None, roi: BBox) -> RoiCrop:
    """Recorta `image` a la ROI de la gondola.

    Una ROI parcialmente fuera de la imagen se recorta a sus limites; una
    ROI completamente fuera, o una imagen None/vacia, lanza ValueError.
    El recorte es una copia (no una vista), para que los filtros que se
    apliquen despues no modifiquen la imagen original.
    """
    check_image(image)

    height, width = image.shape[:2]
    x_min, y_min, x_max, y_max = normalize_roi(roi, width, height)
    cropped = image[y_min:y_max, x_min:x_max].copy()
    return RoiCrop(image=cropped, roi=(x_min, y_min, x_max, y_max))
