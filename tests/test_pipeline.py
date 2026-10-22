import json
from dataclasses import astuple

import numpy as np
import pytest

from src.pipeline import measure_boxes, run_image
from src.postprocessing.availability import compute_availability
from src.postprocessing.shelf_levels import shelf_levels
from src.preprocessing.gondola_segmentation import segment_gondola
from src.preprocessing.image_correction import LensCalibration, correct_image
from src.preprocessing.roi_filter import crop_roi
from tests.pipeline_fixtures import HEIGHT, WIDTH, ColorDetector, distort, gondola

# Repisas 1 y 2 vacias en su 70% central (40% libre de la gondola).
EMPTIED = {1: (0.15, 0.85), 2: (0.15, 0.85)}


def _by_hand(image, calibration=None):
    """Las etapas encadenadas a mano, como indica CLAUDE.md."""
    corrected = correct_image(image, calibration)
    segmentation = segment_gondola(corrected.image)
    crop = crop_roi(corrected.image, segmentation.roi)
    boxes = [crop.to_original(d.bbox) for d in ColorDetector().detect(crop.image)]
    lines = [astuple(line) for line in segmentation.shelf_lines]
    levels = shelf_levels(boxes, lines, segmentation.roi)
    return corrected, segmentation, boxes, compute_availability(boxes, levels)


def test_run_image_matches_the_stages_chained_by_hand():
    image, _ = gondola(EMPTIED)
    _, segmentation, boxes, availability = _by_hand(image)
    result = run_image(image, ColorDetector())
    assert np.allclose(result.products, boxes)
    assert np.allclose(result.roi, segmentation.roi)
    assert result.segmentation_found
    assert result.free_fraction == pytest.approx(availability.free_fraction)
    assert result.critical == availability.critical
    assert [s.level_index for s in result.shelves] == [
        s.level_index for s in availability.shelves
    ]


def test_detector_receives_the_corrected_image_cropped_to_the_roi():
    image, _ = gondola()
    detector = ColorDetector()
    run_image(image, detector, conf=0.4)
    _, segmentation, _, _ = _by_hand(image)
    x_min, y_min, x_max, y_max = segmentation.roi
    crop, conf = detector.calls[0]
    assert crop.shape[:2] == (y_max - y_min, x_max - x_min)
    assert conf == 0.4


def test_full_gondola_has_no_alert():
    result = run_image(gondola()[0], ColorDetector())
    assert not result.critical
    assert result.free_fraction < 0.1


def test_emptying_shelves_creates_gaps_there_and_the_alert():
    result = run_image(gondola(EMPTIED)[0], ColorDetector())
    assert result.critical and result.free_fraction >= 0.3
    assert len([s for s in result.shelves if s.gaps]) == 2
    assert any(not s.gaps for s in result.shelves)


def test_alert_threshold_can_be_changed():
    # CU05 (#44): el umbral es configurable; el % libre no depende de él.
    image = gondola(EMPTIED)[0]
    default = run_image(image, ColorDetector())
    higher = run_image(image, ColorDetector(), critical_free_fraction=default.free_fraction + 0.05)
    assert default.critical and not higher.critical
    assert higher.free_fraction == default.free_fraction


def test_alert_and_free_space_are_reported_only_for_the_whole_gondola():
    # Una repisa vacia en su 70% central no llega al 30% de la gondola.
    result = run_image(gondola({1: (0.15, 0.85)})[0], ColorDetector())
    assert any(s.gaps for s in result.shelves)
    assert not result.critical
    # Por repisa solo va la geometria (contorno y huecos), sin % ni alerta.
    for shelf in result.to_dict()["shelves"]:
        assert set(shelf) == {"level_index", "polygon", "gaps", "product_count"}


def test_without_calibration_gap_polygons_cover_the_free_width():
    # Los huecos y contornos que se informan explican el % de la gondola.
    result = run_image(gondola(EMPTIED)[0], ColorDetector())
    shelf_width = sum(np.ptp(np.array(s.polygon)[:, 0]) for s in result.shelves)
    gap_width = sum(np.ptp(np.array(g)[:, 0]) for s in result.shelves for g in s.gaps)
    assert gap_width / shelf_width == pytest.approx(result.free_fraction)


def test_with_lens_calibration_results_go_back_to_the_original_photo():
    calibration = LensCalibration.approximate(WIDTH, HEIGHT, -0.25)
    photo = distort(gondola({1: (0.15, 0.85)})[0], calibration)
    corrected, _, boxes, availability = _by_hand(photo, calibration)
    result = run_image(photo, ColorDetector(), calibration=calibration)
    assert np.allclose(result.products, [corrected.to_original(b) for b in boxes])
    assert result.free_fraction == pytest.approx(availability.free_fraction)
    for shelf, measured in zip(result.shelves, availability.shelves):
        polygon = np.array(shelf.polygon)
        for corner in corrected.to_original_points(np.array(measured.polygon)):
            assert np.linalg.norm(polygon - corner, axis=1).min() < 1e-6
        # Bordes densificados: con lente se ven curvos, como en la foto.
        assert len(polygon) > 4


def test_without_shelves_falls_back_to_global_analysis():
    blank = np.full((HEIGHT, WIDTH, 3), 128, dtype=np.uint8)
    result = run_image(blank, ColorDetector())
    assert not result.segmentation_found
    assert np.allclose(result.roi, (0, 0, WIDTH, HEIGHT))
    assert len(result.shelves) == 1
    assert result.critical  # sin productos, todo es hueco


def test_stage_times_are_measured():
    times = run_image(gondola()[0], ColorDetector()).times
    parts = (times.correction, times.segmentation, times.detection, times.availability)
    assert all(part >= 0 for part in parts)
    assert times.total == pytest.approx(sum(parts))


def test_result_serializes_to_json():
    result = run_image(gondola(EMPTIED)[0], ColorDetector())
    data = json.loads(json.dumps(result.to_dict()))
    assert data["image_size"] == [WIDTH, HEIGHT]
    assert data["free_fraction"] == pytest.approx(result.free_fraction)
    assert data["critical"] == result.critical
    assert len(data["products"]) == len(result.products)
    assert len(data["shelves"]) == len(result.shelves)
    assert data["shelves"][1]["gaps"] and data["shelves"][1]["polygon"]
    assert set(data["times"]) == {"correction", "segmentation", "detection", "availability", "total"}


def test_measure_boxes_measures_given_boxes_without_a_detector():
    image, truth = gondola(EMPTIED)
    from_truth = measure_boxes(image, truth)
    detected = run_image(image, ColorDetector())
    assert np.allclose(from_truth.products, truth)
    assert from_truth.free_fraction == pytest.approx(detected.free_fraction, abs=0.02)
    assert from_truth.critical == detected.critical
    assert from_truth.times.detection == 0.0
