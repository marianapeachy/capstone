"""Contrato de src/models/detector.py. Usa arquitecturas construidas desde
su YAML con pesos aleatorios (sin descargas, corre offline): se prueba la
interfaz y las coordenadas, no la calidad de la deteccion."""

import numpy as np
import pytest

pytest.importorskip("ultralytics")

from src.models.detector import MAX_DET, Detection, ProductDetector  # noqa: E402
from src.preprocessing.roi_filter import crop_roi  # noqa: E402


@pytest.fixture(scope="module")
def detector():
    return ProductDetector("yolo26n.yaml", device="cpu")


def test_detect_returns_boxes_in_image_pixels(detector):
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    detections = detector.detect(image, conf=0.0)
    assert detections and all(isinstance(d, Detection) for d in detections)
    boxes = np.array([d.bbox for d in detections])
    assert (boxes[:, 0] <= boxes[:, 2]).all() and (boxes[:, 1] <= boxes[:, 3]).all()
    assert (boxes >= 0).all() and (boxes[:, [0, 2]] <= 320).all() and (boxes[:, [1, 3]] <= 240).all()


def test_detect_is_not_truncated_to_the_ultralytics_default_of_300(detector):
    # Con conf=0 la cabeza sin NMS entrega hasta max_det cajas; una gondola
    # llena de SKU-110K supera las 300 del default de Ultralytics.
    image = np.zeros((960, 1280, 3), dtype=np.uint8)
    assert len(detector.detect(image, conf=0.0)) == MAX_DET


def test_detections_map_back_to_the_original_image_through_the_roi(detector):
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    crop = crop_roi(image, (100, 50, 420, 290))
    for detection in detector.detect(crop.image, conf=0.0)[:50]:
        x_min, y_min, x_max, y_max = crop.to_original(detection.bbox)
        assert 100 <= x_min <= x_max <= 420
        assert 50 <= y_min <= y_max <= 290


@pytest.mark.parametrize("image", [None, np.zeros((0, 0, 3), dtype=np.uint8)])
def test_detect_rejects_missing_or_empty_image(detector, image):
    with pytest.raises(ValueError):
        detector.detect(image)


def test_rejects_models_without_the_yolo26_nms_free_head():
    with pytest.raises(ValueError, match="NMS"):
        ProductDetector("yolo11n.yaml", device="cpu")
