import pytest

from src.evaluation.detection_metrics import DetectionMetrics, iou, match_detections


def test_iou_of_identical_boxes_is_one():
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == pytest.approx(1.0)


def test_iou_of_disjoint_boxes_is_zero():
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_iou_of_half_overlapping_boxes():
    # Interseccion 50, union 150.
    assert iou((0, 0, 10, 10), (5, 0, 15, 10)) == pytest.approx(50 / 150)


def test_perfect_detections_give_precision_and_recall_one():
    truth = [(0, 0, 10, 10), (20, 0, 30, 10)]
    metrics = match_detections(truth, truth)
    assert (metrics.true_positives, metrics.false_positives, metrics.false_negatives) == (2, 0, 0)
    assert metrics.precision == 1.0 and metrics.recall == 1.0 and metrics.f1 == 1.0
    assert metrics.mean_iou == pytest.approx(1.0)


def test_extra_detection_is_a_false_positive_and_missing_one_a_false_negative():
    truth = [(0, 0, 10, 10), (20, 0, 30, 10)]
    predicted = [(0, 0, 10, 10), (50, 50, 60, 60)]
    metrics = match_detections(predicted, truth)
    assert (metrics.true_positives, metrics.false_positives, metrics.false_negatives) == (1, 1, 1)
    assert metrics.precision == 0.5 and metrics.recall == 0.5


def test_overlap_below_the_threshold_does_not_match():
    metrics = match_detections([(0, 0, 10, 10)], [(6, 0, 16, 10)], iou_threshold=0.5)
    assert metrics.true_positives == 0


def test_each_annotation_matches_at_most_one_detection_the_best_one():
    truth = [(0, 0, 10, 10)]
    predicted = [(1, 0, 11, 10), (0, 0, 10, 10)]
    metrics = match_detections(predicted, truth)
    assert (metrics.true_positives, metrics.false_positives) == (1, 1)
    assert metrics.mean_iou == pytest.approx(1.0)


def test_no_detections_and_no_annotations_is_not_an_error():
    metrics = match_detections([], [])
    assert metrics.precision == 0.0 and metrics.recall == 0.0 and metrics.mean_iou == 0.0


def test_metrics_add_up_over_images():
    a = match_detections([(0, 0, 10, 10)], [(0, 0, 10, 10)])
    b = match_detections([], [(0, 0, 10, 10)])
    total = DetectionMetrics.total([a, b])
    assert (total.true_positives, total.false_negatives) == (1, 1)
    assert total.recall == 0.5
