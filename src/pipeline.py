"""Pipeline completo de una foto de gondola (item #8 de PROGRESS.md).

Es el unico modulo que conoce todas las etapas; no es una etapa: las
etapas siguen sin importarse entre si (CLAUDE.md). Flujo:

    correct_image -> segment_gondola -> crop_roi -> detector.detect
    -> RoiCrop.to_original -> shelf_levels -> compute_availability

La disponibilidad se calcula en la imagen corregida, donde se segmentaron
las repisas; solo el resultado se lleva a la foto original
(CorrectedImage), con los bordes de repisas y huecos densificados para que
con lente fisheye se vean curvos, como en la foto.

`measure_boxes()` mide cajas dadas (por ejemplo, una anotacion hecha a
mano) en vez de detectarlas: es la referencia de la evaluacion por lotes
(CU07).
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import asdict, astuple, dataclass
from typing import Protocol

import numpy as np

from src.postprocessing.availability import (
    CRITICAL_FREE_FRACTION,  # la app web lo toma de aqui (umbral por defecto de CU05)
    AvailabilityParams,
    GondolaAvailability,
    compute_availability,
)
from src.postprocessing.shelf_levels import shelf_levels
from src.preprocessing.gondola_segmentation import GondolaSegmentation, segment_gondola
from src.preprocessing.image_correction import CorrectedImage, LensCalibration, correct_image
from src.preprocessing.roi_filter import crop_roi

BBox = tuple[float, float, float, float]
Point = tuple[float, float]
Polygon = tuple[Point, ...]

# Puntos por borde al llevar un poligono a la foto original: con lente, un
# borde recto en la imagen corregida es una curva en la original.
EDGE_SAMPLES = 9


class Detector(Protocol):
    """ProductDetector en produccion; cualquier objeto con detect() que
    devuelva elementos con `.bbox` en coordenadas de la imagen recibida."""

    def detect(self, image: np.ndarray, *args, **kwargs) -> Sequence: ...


@dataclass(frozen=True)
class ShelfResult:
    """Geometria de un nivel de repisa en la foto original: el frente
    medido y `gaps`, un poligono por hueco, de izquierda a derecha. Sin %
    libre ni alerta: se informan solo los de la gondola completa
    (PipelineResult)."""

    level_index: int
    polygon: Polygon
    gaps: tuple[Polygon, ...]
    product_count: int


@dataclass(frozen=True)
class StageTimes:
    """Segundos por etapa. `detection` incluye el recorte a la ROI y el
    paso de las cajas a la imagen corregida."""

    correction: float
    segmentation: float
    detection: float
    availability: float

    @property
    def total(self) -> float:
        return self.correction + self.segmentation + self.detection + self.availability


@dataclass(frozen=True)
class PipelineResult:
    """Resultado de una foto, en coordenadas de la foto original.
    `free_fraction` y `critical` (alerta de quiebre) son los de la gondola
    completa; `shelves` solo trae la geometria de la medicion. Con
    `segmentation_found` falso no se encontraron repisas y la gondola se
    midio como un solo nivel (analisis global)."""

    image_size: tuple[int, int]  # (ancho, alto)
    roi: BBox
    products: tuple[BBox, ...]
    shelves: tuple[ShelfResult, ...]
    free_fraction: float
    critical: bool
    segmentation_found: bool
    times: StageTimes

    def to_dict(self) -> dict:
        """Diccionario serializable a JSON."""
        data = asdict(self)
        data["times"]["total"] = self.times.total
        return data


def run_image(
    image: np.ndarray,
    detector: Detector,
    calibration: LensCalibration | None = None,
    conf: float | None = None,
    critical_free_fraction: float | None = None,
) -> PipelineResult:
    """Corre el pipeline sobre una foto BGR. Sin `calibration` solo se
    aplica CLAHE. `conf` se pasa al detector (None: su valor por defecto).
    `critical_free_fraction` es el espacio libre desde el que se alerta
    (None: 30%, el umbral por defecto; lo configura CU05)."""

    def detect(corrected: np.ndarray, segmentation: GondolaSegmentation) -> list[BBox]:
        crop = crop_roi(corrected, segmentation.roi)
        found = detector.detect(crop.image) if conf is None else detector.detect(crop.image, conf)
        return [crop.to_original(d.bbox) for d in found]

    params = AvailabilityParams() if critical_free_fraction is None else AvailabilityParams(
        critical_free_fraction=critical_free_fraction)
    return _measure(image, calibration, detect, params=params)


def measure_boxes(image: np.ndarray, boxes: Sequence[BBox]) -> PipelineResult:
    """Mide cajas dadas en vez de detectarlas, con la misma segmentacion y
    el mismo calculo de disponibilidad que run_image(). Las cajas van en
    coordenadas de la foto; sin calibracion, coinciden con las de la imagen
    corregida."""
    given = [tuple(float(v) for v in box) for box in boxes]
    return _measure(image, None, given=given)


def _measure(
    image: np.ndarray,
    calibration: LensCalibration | None,
    get_boxes: Callable[[np.ndarray, GondolaSegmentation], list[BBox]] | None = None,
    given: list[BBox] | None = None,
    params: AvailabilityParams = AvailabilityParams(),
) -> PipelineResult:
    """Con `get_boxes` detecta (y mide su tiempo); con `given`, usa esas
    cajas y la deteccion queda en 0 segundos."""
    start = time.perf_counter()
    corrected = correct_image(image, calibration)
    corrected_at = time.perf_counter()
    segmentation = segment_gondola(corrected.image)
    segmented_at = time.perf_counter()
    boxes = get_boxes(corrected.image, segmentation) if get_boxes is not None else given
    detected_at = time.perf_counter() if get_boxes is not None else segmented_at
    lines = [astuple(line) for line in segmentation.shelf_lines]
    levels = shelf_levels(boxes, lines, segmentation.roi)
    availability = compute_availability(boxes, levels, params)
    result = _to_original(image, corrected, segmentation, boxes, availability)
    finished_at = time.perf_counter()
    times = StageTimes(
        correction=corrected_at - start,
        segmentation=segmented_at - corrected_at,
        detection=detected_at - segmented_at,
        availability=finished_at - detected_at,
    )
    return PipelineResult(**result, times=times)


def _to_original(
    image: np.ndarray,
    corrected: CorrectedImage,
    segmentation: GondolaSegmentation,
    boxes: list[BBox],
    availability: GondolaAvailability,
) -> dict:
    height, width = image.shape[:2]
    shelves = tuple(
        ShelfResult(
            level_index=int(shelf.level_index),
            polygon=_points(corrected, _densify(shelf.polygon)),
            gaps=tuple(
                _points(corrected, _gap_outline(shelf.polygon, start, end))
                for start, end in shelf.gaps
            ),
            product_count=int(shelf.product_count),
        )
        for shelf in availability.shelves
    )
    return {
        "image_size": (int(width), int(height)),
        "roi": _bbox(corrected.to_original(segmentation.roi)),
        "products": tuple(_bbox(corrected.to_original(box)) for box in boxes),
        "shelves": shelves,
        "free_fraction": float(availability.free_fraction),
        "critical": bool(availability.critical),
        "segmentation_found": bool(segmentation.found),
    }


def _bbox(box: Sequence[float]) -> BBox:
    return tuple(float(v) for v in box)


def _points(corrected: CorrectedImage, points: np.ndarray) -> Polygon:
    return tuple((float(x), float(y)) for x, y in corrected.to_original_points(points))


def _densify(polygon: Sequence[Point]) -> np.ndarray:
    """Contorno cerrado con EDGE_SAMPLES puntos por borde (sin repetir el
    vertice final de cada borde)."""
    corners = np.asarray(polygon, dtype=float)
    t = np.linspace(0.0, 1.0, EDGE_SAMPLES, endpoint=False)[:, None]
    return np.concatenate(
        [a + t * (b - a) for a, b in zip(corners, np.roll(corners, -1, axis=0))]
    )


def _gap_outline(polygon: Sequence[Point], start: float, end: float) -> np.ndarray:
    """Tramo del nivel (sup. izq., sup. der., inf. der., inf. izq.) entre
    x = start y x = end, siguiendo sus bordes superior e inferior."""
    (x0, top0), (x1, top1), (_, bottom1), (_, bottom0) = polygon
    xs = np.linspace(start, end, EDGE_SAMPLES)
    t = (xs - x0) / (x1 - x0)
    top = np.column_stack((xs, top0 + t * (top1 - top0)))
    bottom = np.column_stack((xs, bottom0 + t * (bottom1 - bottom0)))[::-1]
    return np.concatenate((top, bottom))
