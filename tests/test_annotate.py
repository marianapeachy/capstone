from dataclasses import replace

import numpy as np

from src.pipeline import run_image
from src.reporting.annotate import draw_availability
from tests.pipeline_fixtures import ColorDetector, gondola

EMPTIED = {1: (0.15, 0.85), 2: (0.15, 0.85)}


def _redness(pixel: np.ndarray) -> int:
    b, g, r = (int(v) for v in pixel)
    return r - max(g, b)


def _banner_color(view: np.ndarray) -> np.ndarray:
    """Color medio del cartel superior (franja de arriba de la vista)."""
    return view[: view.shape[0] // 40].reshape(-1, 3).mean(axis=0)


def test_view_has_the_photo_shape_and_does_not_modify_it():
    image, _ = gondola(EMPTIED)
    original = image.copy()
    view = draw_availability(image, run_image(image, ColorDetector()))
    assert view.shape == image.shape
    assert np.array_equal(image, original)


def test_gaps_are_painted_red():
    image, _ = gondola(EMPTIED)
    result = run_image(image, ColorDetector())
    view = draw_availability(image, result)
    gap = np.array(next(s for s in result.shelves if s.gaps).gaps[0])
    x, y = (int(v) for v in gap.mean(axis=0))
    assert _redness(view[y, x]) > _redness(image[y, x]) + 40


def test_shelf_label_is_not_hidden_by_the_banner():
    image, _ = gondola()
    result = run_image(image, ColorDetector())
    top = min(y for _, y in result.shelves[0].polygon)
    shifted = replace(result, shelves=(replace(result.shelves[0], polygon=tuple(
        (x, y - top) for x, y in result.shelves[0].polygon)), *result.shelves[1:]))
    view = draw_availability(image, shifted)
    # Fin del cartel: primera fila del borde derecho con otro color.
    column = view[: view.shape[0] // 4, -2].astype(int)
    banner = int(np.argmax(np.any(column != column[0], axis=1)))
    assert banner > 0
    # Bajo el cartel, a la izquierda, esta el recuadro oscuro de "Repisa 1".
    below = view[banner + 2 : banner + 12, 6:40].reshape(-1, 3)
    assert (below.max(axis=1) < 60).mean() > 0.5


def test_banner_is_red_with_alert_and_green_without_it():
    image, _ = gondola(EMPTIED)
    alert = _banner_color(draw_availability(image, run_image(image, ColorDetector())))
    full, _ = gondola()
    ok = _banner_color(draw_availability(full, run_image(full, ColorDetector())))
    assert alert[2] > alert[1]  # BGR: mas rojo que verde
    assert ok[1] > ok[2]
