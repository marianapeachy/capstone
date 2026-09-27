import cv2
import numpy as np
import pytest

from src.preprocessing.image_correction import (
    CorrectedImage,
    LensCalibration,
    apply_clahe,
    correct_image,
    dewarp,
)

HEIGHT, WIDTH = 200, 300


def _low_contrast_gray() -> np.ndarray:
    """Gradiente horizontal comprimido en 100-140, como una gondola en
    sombra."""
    row = np.linspace(100, 140, WIDTH).astype(np.uint8)
    return np.tile(row, (HEIGHT, 1))


def _line_image(y: int) -> np.ndarray:
    """Fondo blanco con una linea horizontal negra en la fila `y`, como el
    borde de una repisa."""
    image = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)
    image[y - 1 : y + 2, :] = 0
    return image


def _grid_points() -> np.ndarray:
    ys, xs = np.mgrid[0:HEIGHT, 0:WIDTH]
    return np.column_stack((xs.ravel(), ys.ravel())).astype(np.float64)


def _distort(image: np.ndarray, calibration: LensCalibration) -> np.ndarray:
    """Simula la foto que tomaria una camara con esa lente: cada pixel de
    la imagen distorsionada toma el valor de su punto sin distorsion."""
    k, d = calibration.camera_matrix, calibration.dist_coeffs
    points = _grid_points().reshape(-1, 1, 2)
    if calibration.fisheye:
        source = cv2.fisheye.undistortPoints(points, k, d, P=k)
    else:
        source = cv2.undistortPoints(points, k, d, P=k)
    maps = source.reshape(HEIGHT, WIDTH, 2).astype(np.float32)
    return cv2.remap(
        image, maps[..., 0], maps[..., 1], cv2.INTER_LINEAR, borderValue=255
    )


def _line_rows(image: np.ndarray, columns: list[int]) -> list[int]:
    return [int(np.argmin(image[:, c])) for c in columns]


# --- CLAHE ---


def test_apply_clahe_enhances_detail_in_shadow_and_keeps_shape():
    # Mitad izquierda en sombra con franjas de 20/28 (ej. empaques al fondo
    # del estante) y mitad derecha iluminada con franjas de 200/208.
    stripes = (np.arange(WIDTH) // 4) % 2 * 8
    image = np.tile(np.where(np.arange(WIDTH) < WIDTH // 2, 20, 200) + stripes, (HEIGHT, 1))
    image = image.astype(np.uint8)
    result = apply_clahe(image)
    assert result.shape == image.shape and result.dtype == np.uint8
    shadow = (slice(None), slice(0, WIDTH // 2 - 16))
    assert result[shadow].std() > 1.2 * image[shadow].std()
    # clip_limit acota la amplificacion (y con ella el ruido): subirlo realza mas.
    stronger = apply_clahe(image, clip_limit=4.0)
    assert stronger[shadow].std() > result[shadow].std()


def test_apply_clahe_bgr_keeps_neutral_colors_neutral():
    # Solo se ecualiza la luminancia: un gris sigue siendo gris.
    image = cv2.cvtColor(_low_contrast_gray(), cv2.COLOR_GRAY2BGR)
    result = apply_clahe(image).astype(int)
    assert result.shape == image.shape
    assert np.abs(result[..., 0] - result[..., 1]).max() <= 2
    assert np.abs(result[..., 1] - result[..., 2]).max() <= 2


def test_apply_clahe_does_not_modify_input():
    image = _low_contrast_gray()
    original = image.copy()
    apply_clahe(image)
    assert np.array_equal(image, original)


@pytest.mark.parametrize(
    ("image", "kwargs", "message"),
    [
        (None, {}, "None"),
        (np.zeros((0, 10), dtype=np.uint8), {}, "vacia"),
        (np.zeros((10, 10), dtype=np.float32), {}, "uint8"),
        (np.zeros((10, 10, 4), dtype=np.uint8), {}, "3 canales"),
        (np.zeros((10, 10), dtype=np.uint8), {"clip_limit": 0}, "clip_limit"),
        (np.zeros((10, 10), dtype=np.uint8), {"tile_grid_size": (0, 8)}, "tile_grid_size"),
    ],
)
def test_apply_clahe_rejects_invalid_input(image, kwargs, message):
    with pytest.raises(ValueError, match=message):
        apply_clahe(image, **kwargs)


# --- Dewarping ---


def test_dewarp_without_distortion_keeps_image_and_coordinates():
    image = _line_image(y=30)
    result = dewarp(image, LensCalibration.approximate(WIDTH, HEIGHT, k1=0.0))
    assert np.abs(result.image.astype(int) - image).max() <= 1
    assert result.to_original((10, 20, 60, 70)) == pytest.approx((10, 20, 60, 70))


def test_dewarp_straightens_shelf_line_curved_by_barrel_distortion():
    calibration = LensCalibration.approximate(WIDTH, HEIGHT, k1=-0.3)
    distorted = _distort(_line_image(y=30), calibration)
    columns = [40, WIDTH // 2, WIDTH - 41]

    curved = _line_rows(distorted, columns)
    assert max(curved) - min(curved) >= 3  # la lente curva la repisa

    straight = _line_rows(dewarp(distorted, calibration).image, columns)
    assert max(straight) - min(straight) <= 1
    assert straight[1] == pytest.approx(30, abs=1)


@pytest.mark.parametrize("fisheye", [False, True])
def test_to_original_points_inverts_undistortion(fisheye):
    if fisheye:
        calibration = LensCalibration(
            camera_matrix=LensCalibration.approximate(WIDTH, HEIGHT, 0.0).camera_matrix,
            dist_coeffs=[0.05, -0.02, 0.0, 0.0],
            fisheye=True,
        )
    else:
        calibration = LensCalibration.approximate(WIDTH, HEIGHT, k1=-0.3)
    k, d = calibration.camera_matrix, calibration.dist_coeffs
    original = np.array([[10.0, 15.0], [150.0, 100.0], [280.0, 190.0], [35.5, 170.25]])
    undistort = cv2.fisheye.undistortPoints if fisheye else cv2.undistortPoints
    corrected = undistort(original.reshape(-1, 1, 2), k, d, P=k).reshape(-1, 2)

    back = CorrectedImage(np.zeros((HEIGHT, WIDTH), np.uint8), calibration)
    assert back.to_original_points(corrected) == pytest.approx(original, abs=0.05)


def test_to_original_bbox_of_full_frame_falls_inside_original_with_barrel():
    # Con barril la salida conserva la escala del centro y pierde borde:
    # el marco completo de la imagen corregida cae dentro de la original.
    calibration = LensCalibration.approximate(WIDTH, HEIGHT, k1=-0.3)
    result = CorrectedImage(np.zeros((HEIGHT, WIDTH), np.uint8), calibration)
    x_min, y_min, x_max, y_max = result.to_original((0, 0, WIDTH - 1, HEIGHT - 1))
    assert 0 < x_min < x_max < WIDTH - 1
    assert 0 < y_min < y_max < HEIGHT - 1


def test_fisheye_dewarp_keeps_size():
    calibration = LensCalibration(
        camera_matrix=LensCalibration.approximate(WIDTH, HEIGHT, 0.0).camera_matrix,
        dist_coeffs=[0.05, -0.02, 0.0, 0.0],
        fisheye=True,
    )
    image = cv2.cvtColor(_line_image(y=30), cv2.COLOR_GRAY2BGR)
    assert dewarp(image, calibration).image.shape == image.shape


def test_dewarp_rejects_none_image():
    with pytest.raises(ValueError, match="None"):
        dewarp(None, LensCalibration.approximate(WIDTH, HEIGHT, k1=0.0))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"camera_matrix": np.eye(2), "dist_coeffs": [0, 0, 0, 0]}, "3x3"),
        ({"camera_matrix": np.eye(3), "dist_coeffs": [0, 0, 0]}, "coeficientes"),
        ({"camera_matrix": np.eye(3), "dist_coeffs": [0] * 5, "fisheye": True}, "fisheye"),
    ],
)
def test_lens_calibration_rejects_invalid_parameters(kwargs, message):
    with pytest.raises(ValueError, match=message):
        LensCalibration(**kwargs)


# --- Correccion completa ---


def test_correct_image_without_calibration_only_applies_clahe():
    image = _low_contrast_gray()
    result = correct_image(image)
    assert result.calibration is None
    assert np.array_equal(result.image, apply_clahe(image))
    assert result.to_original((1.5, 2, 3, 4)) == (1.5, 2, 3, 4)


def test_correct_image_dewarps_before_clahe():
    image = _distort(_line_image(y=30), LensCalibration.approximate(WIDTH, HEIGHT, -0.3))
    calibration = LensCalibration.approximate(WIDTH, HEIGHT, k1=-0.3)
    result = correct_image(image, calibration)
    assert result.calibration is calibration
    assert np.array_equal(result.image, apply_clahe(dewarp(image, calibration).image))
