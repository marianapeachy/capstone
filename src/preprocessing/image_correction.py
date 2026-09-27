"""Correccion de imagen: dewarping (distorsion de lente) y CLAHE.

Primer paso del pre-procesamiento (ver CLAUDE.md): la segmentacion
automatica de la gondola trabaja sobre la imagen ya corregida, porque con
lentes tipo fisheye las lineas de repisa se ven curvas. Orden interno:
primero dewarping y luego CLAHE, para que la ecualizacion por bloques se
calcule sobre la geometria final y no se deforme al remapear.

"Dewarping" aqui es solo la distorsion de lente (radial/tangencial o
fisheye). La perspectiva por angulo oblicuo de la camara no se corrige en
este modulo: requiere conocer el contorno de la gondola, que se obtiene
despues, en la segmentacion.

La imagen corregida tiene el mismo tamano y la misma matriz de camara que
la original (la escala en el centro se conserva). Como toda coordenada
del proyecto va en pixeles de la imagen original, CorrectedImage permite
devolver a ese sistema lo que se detecte sobre la imagen corregida.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from src.preprocessing._validation import check_image

BBox = tuple[float, float, float, float]
Point = tuple[float, float]

# Puntos muestreados por borde al llevar un bbox a la imagen original: con
# distorsion los bordes rectos se vuelven curvas y el extremo de una curva
# no tiene por que caer en una esquina.
_BBOX_EDGE_SAMPLES = 9


@dataclass(frozen=True)
class LensCalibration:
    """Parametros intrinsecos de una camara, en el formato de OpenCV.

    `fisheye=False` usa el modelo pinhole con distorsion radial/tangencial
    (cv2.calibrateCamera: k1, k2, p1, p2[, k3...]); `fisheye=True` usa el
    modelo de cv2.fisheye (cv2.fisheye.calibrate: k1..k4). Los valores
    reales salen de calibrar cada camara con un tablero de ajedrez.
    """

    camera_matrix: np.ndarray
    dist_coeffs: np.ndarray
    fisheye: bool = False

    def __post_init__(self) -> None:
        camera_matrix = np.asarray(self.camera_matrix, dtype=np.float64)
        dist_coeffs = np.asarray(self.dist_coeffs, dtype=np.float64).reshape(-1)
        if camera_matrix.shape != (3, 3):
            raise ValueError(
                f"camera_matrix debe ser 3x3, tiene shape {camera_matrix.shape}"
            )
        expected = (4,) if self.fisheye else (4, 5, 8, 12, 14)
        if dist_coeffs.size not in expected:
            modelo = "fisheye" if self.fisheye else "pinhole"
            raise ValueError(
                f"El modelo {modelo} acepta {expected} coeficientes de "
                f"distorsion, se recibieron {dist_coeffs.size}"
            )
        object.__setattr__(self, "camera_matrix", camera_matrix)
        object.__setattr__(self, "dist_coeffs", dist_coeffs)

    @classmethod
    def approximate(cls, width: int, height: int, k1: float) -> LensCalibration:
        """Calibracion generica para cuando no hay una real: centro optico
        en el centro de la imagen, focal = lado mayor (~53 grados de campo
        horizontal) y un unico coeficiente radial `k1`. Con k1 < 0 corrige
        distorsion de barril (la tipica de gran angular); k1 = 0 no cambia
        la imagen. Pensada para ajustar k1 a ojo mientras no existan los
        parametros reales de las camaras de Walmart."""
        if width <= 0 or height <= 0:
            raise ValueError(f"Tamano de imagen invalido: {width}x{height}")
        focal = float(max(width, height))
        camera_matrix = np.array(
            [[focal, 0.0, (width - 1) / 2], [0.0, focal, (height - 1) / 2], [0.0, 0.0, 1.0]]
        )
        return cls(camera_matrix=camera_matrix, dist_coeffs=np.array([k1, 0.0, 0.0, 0.0]))


@dataclass(frozen=True)
class CorrectedImage:
    """Imagen corregida junto con la calibracion usada (None si no se
    quito distorsion), para volver a coordenadas de la imagen original."""

    image: np.ndarray
    calibration: LensCalibration | None = None

    def to_original_points(self, points: np.ndarray) -> np.ndarray:
        """Lleva puntos (N, 2) de la imagen corregida a la original
        aplicando el modelo de distorsion hacia adelante."""
        points = np.asarray(points, dtype=np.float64).reshape(-1, 2)
        if self.calibration is None or points.size == 0:
            return points.copy()
        k = self.calibration.camera_matrix
        normalized = np.column_stack(
            ((points[:, 0] - k[0, 2]) / k[0, 0], (points[:, 1] - k[1, 2]) / k[1, 1])
        )
        if self.calibration.fisheye:
            distorted = cv2.fisheye.distortPoints(
                normalized.reshape(-1, 1, 2), k, self.calibration.dist_coeffs
            )
        else:
            object_points = np.column_stack((normalized, np.ones(len(normalized))))
            distorted, _ = cv2.projectPoints(
                object_points, np.zeros(3), np.zeros(3), k, self.calibration.dist_coeffs
            )
        return distorted.reshape(-1, 2)

    def to_original(self, bbox: BBox) -> BBox:
        """Lleva un bbox [x_min, y_min, x_max, y_max] de la imagen corregida
        a la original: el menor rectangulo que contiene su borde deformado."""
        x_min, y_min, x_max, y_max = bbox
        if self.calibration is None:
            return (x_min, y_min, x_max, y_max)
        xs = np.linspace(x_min, x_max, _BBOX_EDGE_SAMPLES)
        ys = np.linspace(y_min, y_max, _BBOX_EDGE_SAMPLES)
        border = np.concatenate(
            [
                np.column_stack((xs, np.full_like(xs, y_min))),
                np.column_stack((xs, np.full_like(xs, y_max))),
                np.column_stack((np.full_like(ys, x_min), ys)),
                np.column_stack((np.full_like(ys, x_max), ys)),
            ]
        )
        mapped = self.to_original_points(border)
        return (
            float(mapped[:, 0].min()),
            float(mapped[:, 1].min()),
            float(mapped[:, 0].max()),
            float(mapped[:, 1].max()),
        )


def dewarp(image: np.ndarray | None, calibration: LensCalibration) -> CorrectedImage:
    """Quita la distorsion de lente. La salida conserva tamano y matriz de
    camara, asi que con distorsion de barril se pierde parte del borde de
    la imagen original (no quedan zonas negras en las esquinas)."""
    check_image(image)
    k = calibration.camera_matrix
    if calibration.fisheye:
        corrected = cv2.fisheye.undistortImage(image, k, calibration.dist_coeffs, Knew=k)
    else:
        corrected = cv2.undistort(image, k, calibration.dist_coeffs)
    return CorrectedImage(image=corrected, calibration=calibration)


def apply_clahe(
    image: np.ndarray | None,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
) -> np.ndarray:
    """Ecualizacion adaptativa de contraste (CLAHE) contra sombras y
    reflejos. En BGR se aplica solo a la luminancia (canal L de Lab) para
    no alterar el color de los empaques. Devuelve una imagen nueva del
    mismo tamano; la de entrada no se modifica."""
    check_image(image)
    if image.dtype != np.uint8:
        raise ValueError(f"CLAHE requiere una imagen uint8, se recibio {image.dtype}")
    if clip_limit <= 0:
        raise ValueError(f"clip_limit debe ser > 0, se recibio {clip_limit}")
    if len(tile_grid_size) != 2 or min(tile_grid_size) < 1:
        raise ValueError(f"tile_grid_size invalido: {tile_grid_size!r}")

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tuple(tile_grid_size))
    if image.ndim == 2:
        return clahe.apply(image)
    if image.shape[2] != 3:
        raise ValueError(
            f"Se esperaba una imagen BGR de 3 canales, tiene {image.shape[2]}"
        )
    lightness, a, b = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2LAB))
    return cv2.cvtColor(cv2.merge((clahe.apply(lightness), a, b)), cv2.COLOR_LAB2BGR)


def correct_image(
    image: np.ndarray | None,
    calibration: LensCalibration | None = None,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
) -> CorrectedImage:
    """Correccion completa: dewarping (si hay calibracion) y luego CLAHE.
    Sin calibracion solo se aplica CLAHE y las coordenadas no cambian."""
    check_image(image)
    corrected = dewarp(image, calibration) if calibration is not None else CorrectedImage(image)
    return CorrectedImage(
        image=apply_clahe(corrected.image, clip_limit, tile_grid_size),
        calibration=calibration,
    )
