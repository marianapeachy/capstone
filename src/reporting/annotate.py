"""Vista limpia del resultado sobre la foto original: huecos en rojo,
contorno y porcentaje libre de cada repisa, y un cartel con la alerta de
la gondola. Sin cajas de productos ni ROI: es la imagen para mostrar al
negocio (reporting).

Recibe el resultado del pipeline (`src.pipeline.PipelineResult`), un
dataclass con datos simples; no importa las otras etapas.
"""

from __future__ import annotations

import cv2
import numpy as np

RED = (0, 0, 230)
GREEN = (0, 150, 0)
WHITE = (255, 255, 255)
DARK = (30, 30, 30)
GAP_ALPHA = 0.45
FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_availability(image: np.ndarray, result) -> np.ndarray:
    """Copia de `image` (la foto original, BGR) con el resultado dibujado."""
    view = image.copy()
    height, width = view.shape[:2]
    scale = max(0.4, width / 1600)
    thickness = max(1, round(scale * 2))

    overlay = view.copy()
    for shelf in result.shelves:
        for gap in shelf.gaps:
            cv2.fillPoly(overlay, [_int_points(gap)], RED)
    view = cv2.addWeighted(overlay, GAP_ALPHA, view, 1 - GAP_ALPHA, 0)

    banner = max(24, height // 16)
    for number, shelf in enumerate(result.shelves, start=1):
        points = _int_points(shelf.polygon)
        cv2.polylines(view, [points], True, WHITE, thickness, cv2.LINE_AA)
        x, y = points.min(axis=0)
        # Una repisa que empieza en el borde superior de la foto quedaria
        # con la etiqueta bajo el cartel.
        _label(view, f"Repisa {number} - {shelf.free_fraction:.0%} libre",
               (max(0, int(x)) + 4, max(int(y), banner) + 4), scale * 0.8, thickness, DARK)

    if result.critical:
        text, color = f"QUIEBRE DE STOCK - {result.free_fraction:.0%} libre", RED
    else:
        text, color = f"OK - {result.free_fraction:.0%} libre", GREEN
    if not result.segmentation_found:
        text += " (sin repisas: analisis global)"
    cv2.rectangle(view, (0, 0), (width, banner), color, -1)
    (_, text_height), _ = cv2.getTextSize(text, FONT, scale, thickness)
    cv2.putText(view, text, (int(banner * 0.4), (banner + text_height) // 2),
                FONT, scale, WHITE, thickness, cv2.LINE_AA)
    return view


def _int_points(polygon) -> np.ndarray:
    return np.round(np.asarray(polygon, dtype=float)).astype(np.int32)


def _label(view: np.ndarray, text: str, origin: tuple[int, int], scale: float,
           thickness: int, background: tuple[int, int, int]) -> None:
    """Texto blanco sobre un recuadro oscuro, con su esquina superior
    izquierda en `origin`."""
    (w, h), baseline = cv2.getTextSize(text, FONT, scale, thickness)
    x, y = origin
    cv2.rectangle(view, (x, y), (x + w + 6, y + h + baseline + 6), background, -1)
    cv2.putText(view, text, (x + 3, y + h + 3), FONT, scale, WHITE, thickness, cv2.LINE_AA)
