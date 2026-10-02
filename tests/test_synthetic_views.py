import numpy as np
import pytest

from src.datasets.synthetic import oblique_view


def test_no_rotation_keeps_image_and_boxes():
    image = np.random.default_rng(0).integers(0, 255, (300, 400, 3), dtype=np.uint8)
    boxes = [(10, 20, 60, 90), (200, 100, 250, 180)]
    warped, moved = oblique_view(image, boxes, yaw_deg=0)
    assert warped.shape == image.shape
    np.testing.assert_allclose(moved, boxes, atol=1e-6)


def test_boxes_follow_the_warped_pixels():
    image = np.zeros((400, 600, 3), dtype=np.uint8)
    box = (380, 250, 460, 330)
    image[250:330, 380:460] = 255
    warped, moved = oblique_view(image, [box], yaw_deg=25, pitch_deg=10)
    ys, xs = np.nonzero(warped[..., 0] > 127)
    x_min, y_min, x_max, y_max = moved[0]
    assert xs.min() >= x_min - 2 and xs.max() <= x_max + 2
    assert ys.min() >= y_min - 2 and ys.max() <= y_max + 2
    # El rectangulo envuelve bien al producto (no es mucho mas grande).
    assert (x_max - x_min) <= 1.2 * (xs.max() - xs.min() + 1)


def test_yaw_tilts_horizontal_shelves():
    # Dos productos sobre la misma repisa horizontal: con la camara girada
    # hacia un lado, sus bases quedan a distinta altura.
    image = np.full((400, 600, 3), 128, dtype=np.uint8)
    boxes = [(50, 200, 100, 300), (500, 200, 550, 300)]
    _, moved = oblique_view(image, boxes, yaw_deg=30, pitch_deg=-15)
    assert len(moved) == 2
    assert abs(moved[0][3] - moved[1][3]) > 10


def test_crop_has_no_black_borders():
    image = np.full((300, 400, 3), 128, dtype=np.uint8)
    warped, _ = oblique_view(image, [], yaw_deg=35, pitch_deg=-20)
    assert warped.max(axis=2).min() > 0
    assert max(warped.shape[:2]) == 400


def test_drops_boxes_left_out_of_the_crop():
    image = np.full((300, 400, 3), 128, dtype=np.uint8)
    corner = (0, 0, 30, 30)  # la esquina queda fuera del recorte
    center = (180, 130, 220, 170)
    _, moved = oblique_view(image, [corner, center], yaw_deg=35, pitch_deg=-20)
    assert len(moved) == 1


def test_rejects_rotation_out_of_view():
    image = np.full((300, 400, 3), 128, dtype=np.uint8)
    with pytest.raises(ValueError):
        oblique_view(image, [], yaw_deg=80)
