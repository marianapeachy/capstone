import math

import numpy as np
import pytest

from src.evaluation.segmentation_proxy import (
    area_fraction,
    centers_inside_fraction,
    resting_on_lines_fraction,
    supported_lines_fraction,
)
from src.preprocessing.gondola_segmentation import ShelfLine

SHELF = ShelfLine(x_min=0, x_max=100, slope=0.0, intercept=50)
# Tres productos apoyados en la repisa (base en y=50) y uno flotando.
BOXES = np.array(
    [[0, 20, 10, 50], [20, 25, 30, 51], [40, 30, 50, 49], [60, 0, 70, 20]], dtype=float
)


def test_centers_inside_fraction_counts_box_centers():
    # Centros en y = 35, 38, 39.5 y 10: solo el primero y el ultimo quedan dentro.
    assert centers_inside_fraction((0, 0, 100, 36), BOXES) == pytest.approx(0.5)
    assert math.isnan(centers_inside_fraction((0, 0, 1, 1), np.empty((0, 4))))


def test_area_fraction_relative_to_image():
    assert area_fraction((0, 0, 50, 40), width=100, height=80) == pytest.approx(0.25)


def test_resting_on_lines_fraction_uses_box_bottoms():
    assert resting_on_lines_fraction([SHELF], BOXES, tolerance_px=2) == pytest.approx(0.75)
    assert resting_on_lines_fraction([], BOXES, tolerance_px=2) == 0.0


def test_resting_ignores_boxes_outside_the_line_extent():
    short = ShelfLine(x_min=0, x_max=12, slope=0.0, intercept=50)
    assert resting_on_lines_fraction([short], BOXES, tolerance_px=2) == pytest.approx(0.25)


def test_supported_lines_fraction_flags_lines_without_products():
    empty = ShelfLine(x_min=0, x_max=100, slope=0.0, intercept=90)
    assert supported_lines_fraction([SHELF, empty], BOXES, tolerance_px=2) == 0.5
    assert math.isnan(supported_lines_fraction([], BOXES, tolerance_px=2))
