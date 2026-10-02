"""Vistas sinteticas en angulo de una foto anotada (item #22; base del paso
3 del item #14, imagenes "tipo CCTV").

oblique_view() simula girar la camara alrededor de su centro optico
(hacia un lado y hacia abajo, como una camara de sala que mira el pasillo
en diagonal). Para una camara que solo gira, la imagen nueva es una
homografia de la original, H = K R K^-1, sin necesidad de conocer la
profundidad de la escena. Las anotaciones se transforman con la misma
homografia: el bbox de cada producto es el rectangulo que contiene sus
cuatro esquinas transformadas.

La foto girada queda como un cuadrilatero con bordes negros alrededor; se
recorta al mayor rectangulo alineado dentro de el, para que esos bordes
(rectas inclinadas con un salto fuerte de brillo) no parezcan repisas.

Licencias: solo para datasets que permiten modificar sus fotos (Kaggle
supermarket-shelves es CC0; SHARD y Roboflow, CC BY 4.0). SKU-110K
prohibe crear obras derivadas de sus fotos: no usar con el.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import cv2
import numpy as np

BBox = tuple[float, float, float, float]

# Fraccion minima del area de un bbox transformado que debe quedar dentro
# del recorte para conservarlo.
MIN_VISIBLE = 0.5


def oblique_view(
    image: np.ndarray,
    boxes: Sequence[BBox] | np.ndarray,
    yaw_deg: float,
    pitch_deg: float = 0.0,
    focal: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Imagen vista con la camara girada `yaw_deg` hacia un lado y
    `pitch_deg` hacia abajo, y sus bbox [x_min, y_min, x_max, y_max] en
    la imagen nueva (se descartan los que quedan fuera en mas de la
    mitad). `focal` en pixeles; por defecto, el ancho de la imagen (campo
    de vision horizontal de ~53 grados)."""
    if image is None or image.size == 0:
        raise ValueError("Imagen vacia.")
    height, width = image.shape[:2]
    focal = float(focal or width)
    camera = np.array([[focal, 0, width / 2], [0, focal, height / 2], [0, 0, 1]])
    homography = camera @ _rotation(yaw_deg, pitch_deg) @ np.linalg.inv(camera)

    corners = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=float)
    top_left, top_right, bottom_right, bottom_left = _transform(homography, corners)
    x_min = max(top_left[0], bottom_left[0])
    x_max = min(top_right[0], bottom_right[0])
    y_min = max(top_left[1], top_right[1])
    y_max = min(bottom_left[1], bottom_right[1])
    if not (x_max - x_min > 1 and y_max - y_min > 1):
        raise ValueError("El giro es demasiado grande: la imagen sale de cuadro.")
    # Traslada el recorte al origen y lo escala para conservar el lado mayor.
    scale = max(width, height) / max(x_max - x_min, y_max - y_min)
    fit = np.array([[scale, 0, -x_min * scale], [0, scale, -y_min * scale], [0, 0, 1]])
    homography = fit @ homography
    size = (round((x_max - x_min) * scale), round((y_max - y_min) * scale))
    warped = cv2.warpPerspective(image, homography, size, flags=cv2.INTER_LINEAR)

    boxes = np.asarray(boxes, dtype=float).reshape(-1, 4) if len(boxes) else np.empty((0, 4))
    if len(boxes) == 0:
        return warped, boxes
    box_corners = np.stack(
        [boxes[:, [0, 1]], boxes[:, [2, 1]], boxes[:, [2, 3]], boxes[:, [0, 3]]], axis=1
    )
    moved = _transform(homography, box_corners.reshape(-1, 2)).reshape(-1, 4, 2)
    out = np.column_stack([moved[..., 0].min(1), moved[..., 1].min(1), moved[..., 0].max(1), moved[..., 1].max(1)])
    clipped = out.copy()
    clipped[:, [0, 2]] = clipped[:, [0, 2]].clip(0, size[0])
    clipped[:, [1, 3]] = clipped[:, [1, 3]].clip(0, size[1])
    area = (out[:, 2] - out[:, 0]) * (out[:, 3] - out[:, 1])
    visible = (clipped[:, 2] - clipped[:, 0]) * (clipped[:, 3] - clipped[:, 1])
    return warped, clipped[visible >= MIN_VISIBLE * area]


def _rotation(yaw_deg: float, pitch_deg: float) -> np.ndarray:
    yaw, pitch = math.radians(yaw_deg), math.radians(pitch_deg)
    around_y = np.array(
        [[math.cos(yaw), 0, math.sin(yaw)], [0, 1, 0], [-math.sin(yaw), 0, math.cos(yaw)]]
    )
    around_x = np.array(
        [[1, 0, 0], [0, math.cos(pitch), -math.sin(pitch)], [0, math.sin(pitch), math.cos(pitch)]]
    )
    return around_x @ around_y


def _transform(homography: np.ndarray, points: np.ndarray) -> np.ndarray:
    return cv2.perspectiveTransform(points.reshape(-1, 1, 2).astype(np.float64), homography).reshape(-1, 2)
