import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def prep():
    spec = importlib.util.spec_from_file_location("prepare_finetune_dataset", ROOT / "scripts" / "prepare_finetune_dataset.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_train_and_test_photos_are_disjoint_and_exclude_out_of_scope(prep):
    train, test = set(prep.TRAIN_PHOTOS), set(prep.TEST_PHOTOS)
    assert len(train) == 24 and len(test) == 12
    assert not train & test
    assert not train & set(prep.OUT_OF_SCOPE)
    assert "035" not in train | test  # repite la 004


def test_views_resize_then_rotate_with_boxes(prep):
    image = np.full((2000, 3000, 3), 128, dtype=np.uint8)
    boxes = np.array([[100.0, 200.0, 400.0, 600.0], [1500.0, 800.0, 1800.0, 1200.0]])
    views = prep.views(image, boxes, max_side=1500)
    assert [name for name, _, _ in views] == ["f", "y20", "y35"]
    frontal, frontal_boxes = views[0][1], views[0][2]
    assert max(frontal.shape[:2]) == 1500
    np.testing.assert_allclose(frontal_boxes[0], [50, 100, 200, 300])
    for _, img, b in views[1:]:
        assert len(b) == 2 and (b[:, 2] <= img.shape[1] + 1e-6).all()


def test_with_noise_keeps_the_views_and_adds_degraded_copies_with_the_same_boxes(prep):
    image = np.full((200, 300, 3), 128, dtype=np.uint8)
    boxes = np.array([[10.0, 20.0, 60.0, 90.0]])
    clean = [("f", image, boxes), ("y20", image, boxes)]
    out = prep.with_noise(clean, np.random.default_rng(0), copies=2)
    assert [name for name, _, _ in out] == ["f", "y20", "f_ruido1", "f_ruido2", "y20_ruido1", "y20_ruido2"]
    assert out[:2] == clean
    assert all((b == boxes).all() for _, _, b in out)
    assert not np.array_equal(out[2][1], image)
    assert prep.with_noise(clean, np.random.default_rng(0), copies=0) == clean
