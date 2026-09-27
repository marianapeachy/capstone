"""Verifica que el entorno soporte el detector elegido para src/models/:
YOLO26 de Ultralytics (ver CLAUDE.md). Construye la arquitectura desde su
YAML con pesos aleatorios, sin descargar nada, asi que corre offline.
"""

import numpy as np
import pytest

ultralytics = pytest.importorskip("ultralytics")

MIN_ULTRALYTICS = (8, 4, 0)  # primera version que incluye YOLO26


def test_ultralytics_version_supports_yolo26():
    version = tuple(int(p) for p in ultralytics.__version__.split(".")[:3])
    assert version >= MIN_ULTRALYTICS


@pytest.fixture(scope="module")
def yolo26():
    return ultralytics.YOLO("yolo26n.yaml")


def test_yolo26_has_nms_free_head(yolo26):
    head = yolo26.model.model[-1]
    assert head.one2one_cv2 is not None


def test_yolo26_nms_false_uses_end2end_head_and_respects_max_det(yolo26):
    # Por defecto Ultralytics aplica NMS externo incluso en YOLO26; el
    # modo sin NMS (clave para productos apilados) se activa con nms=False.
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    result = yolo26.predict(image, nms=False, conf=0.0, max_det=5, imgsz=320, verbose=False)[0]
    assert yolo26.predictor.model.end2end
    boxes = result.boxes.xyxy.numpy()
    assert boxes.shape == (5, 4)
    # Salida en [x_min, y_min, x_max, y_max] absolutos de la imagen de entrada.
    assert (boxes[:, 0] <= boxes[:, 2]).all() and (boxes[:, 1] <= boxes[:, 3]).all()
    assert (boxes >= 0).all() and (boxes[:, [0, 2]] <= 320).all() and (boxes[:, [1, 3]] <= 240).all()
