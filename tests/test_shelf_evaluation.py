import math

import pytest

from src.datasets.converters import parse_shard_shelf_coords
from src.evaluation.shelf_evaluation import (
    ShelfMatch,
    line_height_fraction,
    match_shelf_heights,
    evaluate_shelf_lines,
    summarize,
)
from src.preprocessing.gondola_segmentation import ShelfLine

HEIGHT = 1000


def _flat(y: float, x_min: float = 0, x_max: float = 800) -> ShelfLine:
    return ShelfLine(x_min=x_min, x_max=x_max, slope=0.0, intercept=y)


def test_parse_shard_shelf_coords_sorts_top_to_bottom():
    # SHARD anota en cualquier orden (casi siempre de abajo hacia arriba).
    assert parse_shard_shelf_coords("0.99,0.8,0.62,0.1") == (0.1, 0.62, 0.8, 0.99)
    assert parse_shard_shelf_coords(" 0.3 ") == (0.3,)


def test_parse_shard_shelf_coords_empty_and_out_of_range():
    assert parse_shard_shelf_coords("") == ()
    with pytest.raises(ValueError):
        parse_shard_shelf_coords("0.5,1.2")


def test_line_height_is_the_average_y_of_a_tilted_line():
    # Recta de y=100 (x=0) a y=300 (x=400): Y promedio 200 = Y en su centro.
    line = ShelfLine(x_min=0, x_max=400, slope=0.5, intercept=100)
    assert line_height_fraction(line, HEIGHT) == pytest.approx(0.2)


def test_match_within_tolerance_one_to_one():
    match = match_shelf_heights([0.10, 0.52, 0.90], [0.12, 0.50, 0.70], tolerance=0.03)
    assert match == ShelfMatch(tp=2, fp=1, fn=1)


def test_one_prediction_matches_at_most_one_shelf():
    # Dos repisas anotadas cerca de una sola linea: la segunda es un FN.
    assert match_shelf_heights([0.50], [0.49, 0.52], tolerance=0.03) == ShelfMatch(1, 0, 1)
    # Dos lineas sobre la misma repisa: la segunda es un FP.
    assert match_shelf_heights([0.49, 0.52], [0.50], tolerance=0.03) == ShelfMatch(1, 1, 0)


def test_matching_maximizes_pairs_not_nearest_first():
    # Emparejar primero lo mas cercano (0.30-0.31) dejaria sin par a 0.27 y
    # 0.34; el optimo empareja 0.27-0.30 y 0.31-0.34.
    match = match_shelf_heights([0.27, 0.31], [0.30, 0.34], tolerance=0.035)
    assert match == ShelfMatch(tp=2, fp=0, fn=0)


def test_match_accepts_unsorted_inputs():
    assert match_shelf_heights([0.9, 0.1], [0.1, 0.9], tolerance=0.01) == ShelfMatch(2, 0, 0)


def test_shelf_match_scores():
    match = ShelfMatch(tp=3, fp=1, fn=2)
    assert match.precision == pytest.approx(0.75)
    assert match.recall == pytest.approx(0.6)
    assert match.f1 == pytest.approx(2 * 3 / (2 * 3 + 1 + 2))


def test_shelf_match_scores_without_lines_or_shelves():
    nothing_found = ShelfMatch(tp=0, fp=0, fn=4)
    assert math.isnan(nothing_found.precision)
    assert nothing_found.recall == 0.0 and nothing_found.f1 == 0.0
    empty = ShelfMatch(0, 0, 0)
    assert math.isnan(empty.precision) and math.isnan(empty.recall) and math.isnan(empty.f1)


def test_evaluate_shelf_lines_uses_fraction_of_height():
    lines = [_flat(105), _flat(495), _flat(700)]
    match = evaluate_shelf_lines(lines, HEIGHT, (0.1, 0.5, 0.95), tolerance=0.02)
    assert match == ShelfMatch(tp=2, fp=1, fn=1)


def test_evaluate_shelf_lines_can_ignore_image_border():
    # Con margen 0.03 no se evaluan repisas ni lineas pegadas al borde.
    lines = [_flat(10), _flat(500)]
    expected = (0.5, 0.99)
    assert evaluate_shelf_lines(lines, HEIGHT, expected, tolerance=0.02) == ShelfMatch(1, 1, 1)
    assert match_shelf_heights([0.01, 0.5], expected, 0.02, border_margin=0.03) == ShelfMatch(1, 0, 0)
    assert evaluate_shelf_lines(
        lines, HEIGHT, expected, tolerance=0.02, border_margin=0.03
    ) == ShelfMatch(1, 0, 0)


def test_summarize_micro_and_macro():
    matches = [ShelfMatch(2, 0, 0), ShelfMatch(0, 1, 1)]
    summary = summarize(matches)
    assert summary["images"] == 2
    assert (summary["tp"], summary["fp"], summary["fn"]) == (2, 1, 1)
    assert summary["precision"] == pytest.approx(2 / 3)
    assert summary["recall"] == pytest.approx(2 / 3)
    assert summary["f1"] == pytest.approx(2 / 3)
    assert summary["f1_per_image"] == pytest.approx(0.5)  # promedio de 1.0 y 0.0
