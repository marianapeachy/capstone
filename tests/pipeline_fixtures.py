"""Gondola sintetica y detector falso para probar el pipeline sin pesos.

Los productos son bloques de color saturado (con lineas de "texto" del
mismo tono, mas oscuras, para que tengan textura); el fondo, las repisas,
el techo y el piso son grises. El detector falso encuentra los bloques por
saturacion, en la imagen que recibe, como haria YOLO26.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

HEIGHT, WIDTH = 600, 800
CEILING_END = 60
LIPS = (150, 290, 430, 540)  # borde superior de cada repisa
LIP_THICKNESS = 12
COLORS = ((0, 0, 210), (0, 190, 0), (200, 0, 0), (0, 170, 230), (190, 0, 190), (220, 170, 0))

BBox = tuple[float, float, float, float]


def gondola(empty: dict[int, tuple[float, float]] | None = None) -> tuple[np.ndarray, list[BBox]]:
    """Imagen BGR de la gondola y bboxes de sus productos. `empty` vacia
    tramos de repisa: {indice de repisa: (fraccion inicial, fraccion final)
    del ancho}; los productos con el centro en ese tramo no se dibujan."""
    empty = empty or {}
    rng = np.random.default_rng(0)
    image = np.full((HEIGHT, WIDTH, 3), 90, dtype=np.uint8)
    image[:CEILING_END] = 200
    image[LIPS[-1] + LIP_THICKNESS :] = 170
    products: list[BBox] = []
    previous_lip_bottom = CEILING_END + 10
    for shelf, lip in enumerate(LIPS):
        x = 5
        while x < WIDTH - 60:
            width = int(rng.integers(35, 60))
            top = max(previous_lip_bottom + 5, lip - int(rng.integers(60, 110)))
            color = COLORS[int(rng.integers(len(COLORS)))]
            start, end = empty.get(shelf, (2.0, 2.0))
            if not start * WIDTH <= x + width / 2 <= end * WIDTH:
                cv2.rectangle(image, (x, top), (x + width, lip - 1), color, -1)
                dark = tuple(int(c * 0.6) for c in color)
                for text_y in range(top + 8, lip - 8, 9):
                    cv2.line(image, (x + 5, text_y), (x + width - 5, text_y), dark, 1)
                products.append((float(x), float(top), float(x + width), float(lip)))
            x += width + int(rng.integers(4, 12))
        image[lip : lip + LIP_THICKNESS] = 245
        previous_lip_bottom = lip + LIP_THICKNESS
    return image, products


@dataclass(frozen=True)
class FakeDetection:
    bbox: BBox
    score: float = 1.0


class ColorDetector:
    """Detector falso: un producto por mancha de color saturado. Guarda
    la imagen y el `conf` de cada llamada para que los tests los revisen."""

    def __init__(self) -> None:
        self.calls: list[tuple[np.ndarray, float | None]] = []

    def detect(self, image: np.ndarray, conf: float | None = None) -> list[FakeDetection]:
        self.calls.append((image, conf))
        saturation = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:, :, 1]
        mask = (saturation > 120).astype(np.uint8)
        count, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=4)
        return [
            FakeDetection((float(x), float(y), float(x + w), float(y + h)))
            for x, y, w, h, area in stats[1:count]
            if area >= 200
        ]


def distort(image: np.ndarray, calibration) -> np.ndarray:
    """Aplica la distorsion de lente de `calibration` (pinhole) a una
    imagen sin distorsion: lo que veria esa camara."""
    height, width = image.shape[:2]
    xs, ys = np.meshgrid(np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32))
    pixels = np.stack([xs.ravel(), ys.ravel()], axis=1).reshape(-1, 1, 2)
    k = calibration.camera_matrix
    undistorted = cv2.undistortPoints(pixels, k, calibration.dist_coeffs, P=k).reshape(height, width, 2)
    return cv2.remap(image, undistorted[..., 0], undistorted[..., 1], cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REPLICATE)
