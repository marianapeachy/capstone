import numpy as np
import pytest

from src.preprocessing.roi_filter import RoiCrop, crop_roi, normalize_roi


def _bgr_image(height: int = 80, width: int = 100) -> np.ndarray:
    """Imagen BGR sintetica donde cada pixel codifica su posicion, para
    verificar que el recorte toma exactamente la region esperada."""
    ys, xs = np.mgrid[0:height, 0:width]
    return np.stack([xs, ys, np.zeros_like(xs)], axis=-1).astype(np.uint8)


# --- ROI dentro de limites ---


def test_crop_roi_inside_bounds_returns_exact_region():
    image = _bgr_image()
    result = crop_roi(image, (10, 20, 60, 70))
    assert result.roi == (10, 20, 60, 70)
    assert result.image.shape == (50, 50, 3)
    assert tuple(result.image[0, 0]) == (10, 20, 0)
    assert tuple(result.image[-1, -1]) == (59, 69, 0)


def test_crop_roi_supports_grayscale_images():
    image = np.zeros((80, 100), dtype=np.uint8)
    assert crop_roi(image, (0, 0, 30, 40)).image.shape == (40, 30)


def test_crop_roi_returns_copy_not_view():
    image = _bgr_image()
    result = crop_roi(image, (10, 20, 60, 70))
    result.image[:] = 255
    assert tuple(image[20, 10]) == (10, 20, 0)


def test_normalize_roi_swaps_inverted_coordinates():
    assert normalize_roi((60, 70, 10, 20), width=100, height=80) == (10, 20, 60, 70)


def test_normalize_roi_rounds_float_coordinates_outward():
    assert normalize_roi((10.4, 20.6, 59.2, 69.9), width=100, height=80) == (
        10,
        20,
        60,
        70,
    )


def test_to_original_translates_crop_coordinates():
    crop = RoiCrop(image=np.zeros((50, 50, 3), dtype=np.uint8), roi=(10, 20, 60, 70))
    assert crop.to_original((5, 5, 15, 25)) == (15, 25, 25, 45)


# --- ROI fuera de limites ---


def test_crop_roi_partially_outside_is_clipped_to_image():
    image = _bgr_image(height=80, width=100)
    result = crop_roi(image, (-20, -10, 150, 90))
    assert result.roi == (0, 0, 100, 80)
    assert result.image.shape == (80, 100, 3)


@pytest.mark.parametrize(
    "roi",
    [
        (120, 10, 200, 50),  # a la derecha de la imagen
        (-50, -50, -10, -10),  # arriba a la izquierda
        (10, 90, 50, 120),  # bajo la imagen
    ],
)
def test_crop_roi_fully_outside_raises(roi):
    with pytest.raises(ValueError, match="fuera de la imagen"):
        crop_roi(_bgr_image(height=80, width=100), roi)


def test_crop_roi_zero_area_raises():
    with pytest.raises(ValueError, match="fuera de la imagen"):
        crop_roi(_bgr_image(), (30, 30, 30, 60))


def test_normalize_roi_rejects_non_finite_coordinates():
    with pytest.raises(ValueError, match="no finitas"):
        normalize_roi((0, 0, float("nan"), 10), width=100, height=80)


# --- Imagen vacia / None ---


def test_crop_roi_none_image_raises():
    with pytest.raises(ValueError, match="None"):
        crop_roi(None, (0, 0, 10, 10))


@pytest.mark.parametrize(
    "image",
    [
        np.zeros((0, 0, 3), dtype=np.uint8),
        np.zeros((0, 100), dtype=np.uint8),
    ],
)
def test_crop_roi_empty_image_raises(image):
    with pytest.raises(ValueError, match="vacia"):
        crop_roi(image, (0, 0, 10, 10))


def test_crop_roi_rejects_non_array_input():
    with pytest.raises(TypeError):
        crop_roi([[0, 0], [0, 0]], (0, 0, 1, 1))
