import numpy as np
import pytest

from src.postprocessing.availability import (
    CRITICAL_FREE_FRACTION,
    GONDOLA_DEPTH_CM,
    AvailabilityParams,
    compute_availability,
    free_volume_cm3,
)

# Dos niveles de 1000 px de ancho y 200 px de alto.
LEVELS = [(0, 0, 1000, 200), (0, 200, 1000, 400)]


def _row(x_starts, width=100, y_min=50, y_max=200):
    return [(x, y_min, x + width, y_max) for x in x_starts]


def test_full_shelf_has_no_gaps_even_with_spacing_between_products():
    # 10 productos de 90 px separados por 10 px: la separacion no es hueco.
    products = [(x, 50, x + 90, 200) for x in range(5, 1000, 100)]
    result = compute_availability(products, LEVELS[:1])
    assert result.shelves[0].gaps == ()
    assert result.free_fraction == 0.0
    assert not result.critical


def test_gap_of_several_products_is_measured():
    # Faltan los productos de x=300 a x=700 (4 anchos de producto).
    products = _row([0, 100, 200, 700, 800, 900])
    shelf = compute_availability(products, LEVELS[:1]).shelves[0]
    assert shelf.gaps == ((300.0, 700.0),)
    assert shelf.free_fraction == pytest.approx(0.4)
    assert shelf.occupied_fraction == pytest.approx(0.6)
    assert shelf.free_area_px == pytest.approx(400 * 200)
    assert shelf.critical


def test_gaps_at_the_edges_count_within_the_gondola_width():
    # La repisa de arriba esta llena: la gondola mide 1000 px de ancho.
    top = _row(range(0, 1000, 100))
    bottom = _row([200, 300, 400, 500, 600, 700], y_min=250, y_max=400)
    shelf = compute_availability(top + bottom, LEVELS).shelves[1]
    assert shelf.gaps == ((0.0, 200.0), (800.0, 1000.0))


def test_gap_narrower_than_a_product_is_ignored_and_threshold_is_configurable():
    products = _row([0, 100, 200, 350, 450, 550, 650, 750, 850])  # hueco de 50 px
    level = [(0, 0, 950, 200)]
    assert compute_availability(products, level).shelves[0].gaps == ()
    loose = AvailabilityParams(min_gap_products=0.5)
    assert compute_availability(products, level, loose).shelves[0].gaps == ((300.0, 350.0),)


def test_stacked_products_cover_the_same_width_as_a_single_one():
    # Una pila de 3 y una sola unidad baja: ambas ocupan su ancho completo.
    stack = [(0, 50, 100, 100), (0, 100, 100, 150), (0, 150, 100, 200)]
    short = [(100, 170, 200, 200)]
    shelf = compute_availability(stack + short, [(0, 0, 200, 200)]).shelves[0]
    assert shelf.free_fraction == 0.0
    assert shelf.product_count == 4


def test_products_are_assigned_to_their_level():
    top = _row(range(0, 1000, 100), y_min=50, y_max=200)
    bottom = _row([0, 100, 200], y_min=250, y_max=400)
    result = compute_availability(top + bottom, LEVELS)
    assert [s.product_count for s in result.shelves] == [10, 3]
    assert result.shelves[0].free_fraction == 0.0
    assert result.shelves[1].free_fraction == pytest.approx(0.7)
    assert result.critical_shelves == (1,)
    # Frente de la gondola: 700 px libres de 2000 px de repisa.
    assert result.free_fraction == pytest.approx(0.35)
    assert result.critical


def test_small_vertical_overlap_does_not_cover_the_level_above():
    # Productos del nivel inferior que asoman 20 px en el superior (ej.
    # perspectiva): 20 < 0.3 x 170, no ocupan el nivel superior.
    products = _row(range(0, 1000, 100), y_min=180, y_max=350)
    result = compute_availability(products, LEVELS, AvailabilityParams(trim_to_products=False))
    assert result.shelves[0].free_fraction == 1.0
    assert result.shelves[1].free_fraction == 0.0


def test_false_shelf_line_through_products_does_not_create_an_empty_level():
    # La segmentacion corta la fila de productos por la mitad (y=125).
    products = _row(range(0, 1000, 100), y_min=50, y_max=200)
    split = [(0, 0, 1000, 125), (0, 125, 1000, 200)]
    result = compute_availability(products, split)
    assert [s.free_fraction for s in result.shelves] == [0.0, 0.0]


def test_empty_shelf_between_stocked_shelves_is_fully_free():
    levels = LEVELS + [(0, 400, 1000, 600)]
    top = _row(range(0, 1000, 100), y_min=50, y_max=200)
    bottom = _row(range(0, 1000, 100), y_min=450, y_max=600)
    result = compute_availability(top + bottom, levels)
    assert result.shelves[1].gaps == ((0.0, 1000.0),)
    assert result.shelves[1].product_count == 0
    assert result.critical_shelves == (1,)
    assert result.free_fraction == pytest.approx(1 / 3)


def test_gondola_is_trimmed_to_the_products():
    # Techo (nivel 0) y piso (nivel 3) sin productos, y productos solo
    # entre x=200 y x=800: la gondola son los niveles 1 y 2 en ese ancho.
    levels = [(0, 0, 1000, 100), (0, 100, 1000, 300), (0, 300, 1000, 500), (0, 500, 1000, 600)]
    products = _row(range(200, 800, 100), y_min=150, y_max=300) + _row(
        range(200, 800, 100), y_min=350, y_max=500
    )
    result = compute_availability(products, levels)
    assert [s.level_index for s in result.shelves] == [1, 2]
    assert result.shelves[0].bbox == (200.0, 100.0, 800.0, 300.0)
    assert result.free_fraction == 0.0

    untrimmed = compute_availability(products, levels, AvailabilityParams(trim_to_products=False))
    assert [s.level_index for s in untrimmed.shelves] == [0, 1, 2, 3]
    assert untrimmed.free_fraction == pytest.approx(0.7)


def test_no_products_means_everything_is_free():
    result = compute_availability([], LEVELS)
    assert result.free_fraction == 1.0
    assert result.critical
    assert result.free_area_px == pytest.approx(2 * 1000 * 200)


def test_boxes_are_clipped_to_the_level_and_degenerate_boxes_ignored():
    products = [(-50, 50, 500, 200), (500, 50, 1100, 200), (300, 60, 300, 90)]
    shelf = compute_availability(np.array(products), LEVELS[:1]).shelves[0]
    assert shelf.gaps == ()
    assert shelf.product_count == 2


def test_alert_threshold_is_inclusive_at_30_percent():
    assert CRITICAL_FREE_FRACTION == 0.30
    # 600 px libres en la repisa de abajo, de 2000 px de frente.
    top = _row(range(0, 1000, 100))
    bottom = _row([0, 100, 200, 900], y_min=250, y_max=400)
    result = compute_availability(top + bottom, LEVELS)
    assert result.free_fraction == pytest.approx(0.3)
    assert result.critical
    strict = AvailabilityParams(critical_free_fraction=0.31)
    assert not compute_availability(top + bottom, LEVELS, strict).critical


def test_roi_as_single_level_when_segmentation_found_no_shelves():
    products = _row([0, 100, 200, 700], y_min=100, y_max=300)
    result = compute_availability(products, [(0, 0, 1000, 400)])
    assert len(result.shelves) == 1
    assert result.shelves[0].gaps == ((300.0, 700.0),)
    assert result.free_fraction == pytest.approx(0.5)


@pytest.mark.parametrize(
    "levels", [[], [(0, 0, 0, 100)], [(0, 100, 50, 100)], [(0, 0, float("nan"), 10)]]
)
def test_invalid_levels_raise(levels):
    with pytest.raises(ValueError):
        compute_availability([], levels)


def test_non_finite_product_raises():
    with pytest.raises(ValueError):
        compute_availability([(0, 0, float("inf"), 10)], LEVELS)


@pytest.mark.parametrize(
    "kwargs",
    [{"critical_free_fraction": 0}, {"critical_free_fraction": 1.5},
     {"min_gap_products": -1}, {"min_level_overlap": 0}],
)
def test_invalid_params_raise(kwargs):
    with pytest.raises(ValueError):
        AvailabilityParams(**kwargs)


def test_free_volume_uses_the_constant_depth():
    assert GONDOLA_DEPTH_CM == 25.0
    # 400 x 200 px libres a 0.1 cm/px = 40 x 20 cm = 800 cm2 x 25 cm.
    assert free_volume_cm3(400 * 200, 0.1) == pytest.approx(20000.0)
    with pytest.raises(ValueError):
        free_volume_cm3(100, 0)
