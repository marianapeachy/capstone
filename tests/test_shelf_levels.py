import numpy as np
import pytest

from src.postprocessing.availability import compute_availability
from src.postprocessing.shelf_levels import (
    ShelfLevelParams,
    product_rows,
    shelf_levels,
    shelf_lines,
)

# Gondola de 1000 px de ancho con 3 repisas: y = SLOPE * x + b, una cada
# 250 px. Productos de 60 x 150 px apoyados en su repisa (base en la
# recta, a la altura de su centro), uno cada 80 px.
INTERCEPTS = (250.0, 500.0, 750.0)
ROI = (0, 0, 1000, 900)


def gondola(slope: float, skip=lambda shelf, x: False) -> np.ndarray:
    boxes = []
    for shelf, intercept in enumerate(INTERCEPTS):
        for x in range(20, 980 - 60, 80):
            if skip(shelf, x):
                continue
            base = slope * (x + 30) + intercept
            boxes.append((x, base - 150, x + 60, base))
    return np.array(boxes, dtype=float)


@pytest.mark.parametrize("slope", [0.0, 0.1, -0.2, 0.35])
def test_product_rows_finds_each_tilted_shelf(slope):
    rows = sorted(product_rows(gondola(slope)), key=lambda line: line[3])
    assert len(rows) == 3
    for (x_min, x_max, row_slope, intercept), expected in zip(rows, INTERCEPTS):
        assert row_slope == pytest.approx(slope, abs=0.01)
        assert intercept == pytest.approx(expected, abs=5)
        assert x_min == 20 and x_max > 900


def test_product_rows_needs_min_products():
    boxes = gondola(0.2)[:2]
    assert product_rows(boxes) == []
    assert product_rows([]) == []


def test_product_rows_ignores_scattered_products():
    # Productos sueltos a alturas distintas: ninguna fila de 3 alineados.
    boxes = [(0, 0, 50, 100), (300, 400, 350, 520), (700, 100, 750, 330)]
    assert product_rows(boxes) == []


def test_shelf_lines_keep_empty_shelf_from_segmentation():
    # La repisa del medio esta vacia: solo la segmentacion la ve.
    slope = 0.2
    boxes = gondola(slope, skip=lambda shelf, x: shelf == 1)
    empty_shelf = (0.0, 1000.0, slope, INTERCEPTS[1] + 8)
    lines = shelf_lines(boxes, [empty_shelf], (0, 1000))
    assert [round(line[3]) for line in lines] == [250, 508, 750]


def test_shelf_lines_drop_duplicates_and_lines_across_products():
    slope = 0.2
    boxes = gondola(slope)
    duplicate = (0.0, 1000.0, slope, INTERCEPTS[0] + 10)  # borde frontal de la repisa
    across = (0.0, 1000.0, slope, INTERCEPTS[1] - 75)  # mitad de una fila (item #17)
    lines = shelf_lines(boxes, [duplicate, across], (0, 1000))
    assert len(lines) == 3
    assert all(abs(line[2] - slope) < 0.01 for line in lines)


def test_shelf_lines_reject_crossing_lines():
    # Una linea de la segmentacion que cruza una fila dentro del ancho de
    # la gondola daria un nivel invertido.
    boxes = gondola(0.0, skip=lambda shelf, x: shelf > 0)
    crossing = (0.0, 1000.0, -0.3, 400.0)  # pasa por y=250 en x=500
    lines = shelf_lines(boxes, [crossing], (0, 1000))
    assert len(lines) == 1


def test_shelf_levels_without_lines_is_the_roi():
    assert shelf_levels([], [], ROI) == (((0, 0), (1000, 0), (1000, 900), (0, 900)),)


def test_shelf_levels_rejects_empty_roi():
    with pytest.raises(ValueError):
        shelf_levels([], [], (10, 10, 10, 20))


@pytest.mark.parametrize("slope", [0.0, 0.2, -0.3])
def test_tilted_full_gondola_has_no_free_space(slope):
    boxes = gondola(slope)
    levels = shelf_levels(boxes, [], (0, -400, 1000, 1300))  # contiene toda la gondola
    assert len(levels) == 3
    for level in levels:
        (x0, _), (x1, _), _, _ = level
        assert (x0, x1) == (0, 1000)
    result = compute_availability(boxes, levels)
    assert result.free_fraction == pytest.approx(0.0, abs=0.01)
    assert not result.critical
    assert [shelf.product_count for shelf in result.shelves] == [12, 12, 12]


def test_tilted_gap_is_found_on_its_shelf():
    slope = 0.25
    boxes = gondola(slope, skip=lambda shelf, x: shelf == 1 and 300 <= x < 700)
    result = compute_availability(boxes, shelf_levels(boxes, [], ROI))
    assert result.critical_shelves == (1,)
    middle = result.shelves[1]
    assert middle.free_fraction == pytest.approx(420 / 940, abs=0.01)


def test_horizontal_levels_hide_gaps_of_tilted_shelves():
    # El problema que resuelve shelf_levels(): con repisas inclinadas, un
    # nivel horizontal (del rango vertical de una repisa al de la
    # siguiente, como GondolaSegmentation.shelves) se mete en los niveles
    # vecinos, y los productos de la repisa de arriba tapan el hueco.
    slope = 0.25
    boxes = gondola(slope, skip=lambda shelf, x: shelf == 1 and 300 <= x < 700)
    top = [b for b in INTERCEPTS]
    bottom = [slope * 1000 + b for b in INTERCEPTS]
    horizontal = [(0, 0, 1000, bottom[0]), (0, top[0], 1000, bottom[1]), (0, top[1], 1000, bottom[2])]
    flat = compute_availability(boxes, horizontal).shelves[1]
    tilted = compute_availability(boxes, shelf_levels(boxes, [], ROI)).shelves[1]
    assert tilted.critical
    assert flat.free_fraction < 0.1 < tilted.free_fraction


def test_levels_stop_where_the_shelf_leaves_the_image():
    # Con pendiente 0.3, la repisa de arriba sale de la ROI (y < 0) hacia
    # la izquierda: el nivel se mide solo donde se ve.
    slope = 0.3
    boxes = gondola(slope)
    levels = shelf_levels(boxes, [], ROI)
    (x0, _), (x1, _), _, _ = levels[0]
    # Linea central del nivel superior: y = 0.3 x + 250 - 75 >= 0 desde x=-583.
    assert (x0, x1) == (0, 1000)
    roi = (0, 200, 1000, 900)
    (x0, _), (x1, _), _, _ = shelf_levels(boxes, [], roi)[0]
    assert x0 == pytest.approx((200 - 175) / slope)
    assert x1 == 1000


def test_params_validation():
    with pytest.raises(ValueError):
        ShelfLevelParams(row_tolerance=0)
    with pytest.raises(ValueError):
        ShelfLevelParams(max_tilt_deg=90)
    with pytest.raises(ValueError):
        ShelfLevelParams(min_row_products=1)
    with pytest.raises(ValueError):
        ShelfLevelParams(crossing_margin=0.5)
