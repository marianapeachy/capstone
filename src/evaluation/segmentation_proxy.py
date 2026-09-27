"""Metricas aproximadas para evaluar la segmentacion de gondola sin
anotaciones de gondola ni repisa (ningun dataset las trae, ver
docs/datasets.md). Usan las anotaciones que si existen (productos,
espacios vacios y precios) como evidencia indirecta:

- Una ROI buena contiene a todas las anotaciones sin ser la imagen entera.
- Un borde de repisa bien ubicado tiene productos apoyados encima: el
  borde inferior de muchos productos cae cerca de alguna repisa.

No reemplazan un set de validacion etiquetado a mano; sirven para
comparar variantes del metodo y detectar regresiones.
"""

from __future__ import annotations

import math
from typing import Iterable, Protocol

import numpy as np

BBox = tuple[float, float, float, float]


class Line(Protocol):
    x_min: float
    x_max: float

    def y_at(self, x: float) -> float: ...


def centers_inside_fraction(roi: BBox, boxes: np.ndarray) -> float:
    """Fraccion de bboxes (N, 4) cuyo centro cae dentro de la ROI. NaN si
    no hay bboxes."""
    boxes = np.asarray(boxes, dtype=float).reshape(-1, 4)
    if len(boxes) == 0:
        return math.nan
    cx = (boxes[:, 0] + boxes[:, 2]) / 2
    cy = (boxes[:, 1] + boxes[:, 3]) / 2
    x_min, y_min, x_max, y_max = roi
    inside = (cx >= x_min) & (cx <= x_max) & (cy >= y_min) & (cy <= y_max)
    return float(inside.mean())


def area_fraction(roi: BBox, width: int, height: int) -> float:
    """Area de la ROI relativa a la imagen (1.0 = no recorta nada)."""
    x_min, y_min, x_max, y_max = roi
    return max(0.0, x_max - x_min) * max(0.0, y_max - y_min) / (width * height)


def resting_on_lines_fraction(
    lines: Iterable[Line], boxes: np.ndarray, tolerance_px: float
) -> float:
    """Fraccion de bboxes (N, 4) cuyo borde inferior esta a menos de
    `tolerance_px` de alguna repisa (evaluada en el centro del bbox). Mide
    repisas no detectadas (tipo recall). NaN si no hay bboxes."""
    boxes = np.asarray(boxes, dtype=float).reshape(-1, 4)
    if len(boxes) == 0:
        return math.nan
    resting = np.zeros(len(boxes), dtype=bool)
    for line in lines:
        resting |= _resting_on(line, boxes, tolerance_px)
    return float(resting.mean())


def supported_lines_fraction(
    lines: Iterable[Line], boxes: np.ndarray, tolerance_px: float, min_boxes: int = 3
) -> float:
    """Fraccion de repisas con al menos `min_boxes` bboxes apoyados encima.
    Mide repisas falsas, ej. bordes de una fila de productos (tipo
    precision). NaN si no hay repisas."""
    lines = list(lines)
    if not lines:
        return math.nan
    boxes = np.asarray(boxes, dtype=float).reshape(-1, 4)
    return float(
        np.mean([_resting_on(line, boxes, tolerance_px).sum() >= min_boxes for line in lines])
    )


def _resting_on(line: Line, boxes: np.ndarray, tolerance_px: float) -> np.ndarray:
    cx = (boxes[:, 0] + boxes[:, 2]) / 2
    within = (cx >= line.x_min - tolerance_px) & (cx <= line.x_max + tolerance_px)
    line_y = np.array([line.y_at(x) for x in cx])
    return within & (np.abs(line_y - boxes[:, 3]) <= tolerance_px)
