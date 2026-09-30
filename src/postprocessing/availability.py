"""Calculo de disponibilidad de la gondola y alerta de quiebre de stock.

Entrada: las cajas de producto detectadas y los niveles de repisa de la
segmentacion, en el formato estandar [x_min, y_min, x_max, y_max] y en el
mismo sistema de coordenadas: el de la imagen corregida, donde se
segmentaron las repisas (con lente fisheye, en la imagen original las
repisas se ven curvas). Para no depender de src/preprocessing ni de
src/models, los niveles y las cajas llegan como tuplas o arrays.

Metrica: cobertura horizontal por repisa. Las cajas de cada nivel se
proyectan sobre el eje X y lo que queda sin cubrir son los huecos. Solo
cuenta como hueco un tramo libre de al menos `min_gap_products` anchos de
producto (la mediana de los anchos en esa repisa): la separacion normal
entre productos no es espacio vacio. La altura de los productos no se
mide: una repisa de productos bajos o una pila a la que le quedan pocas
unidades sigue con producto disponible, y el eje vertical es el que mas
deforma una camara de sala (vista alta u oblicua).

Alerta: espacio libre >= 30% del frente de la gondola (metros lineales de
repisa). Profundidad constante de 25 cm para el volumen del Nivel 1 (ver
CLAUDE.md).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

BBox = tuple[float, float, float, float]
Gap = tuple[float, float]

# Profundidad de toda gondola (constante global, no se estima).
GONDOLA_DEPTH_CM = 25.0
# Fraccion del frente libre desde la que se alerta un quiebre de stock.
CRITICAL_FREE_FRACTION = 0.30


@dataclass(frozen=True)
class AvailabilityParams:
    """critical_free_fraction: espacio libre desde el que se alerta.
    min_gap_products: ancho minimo de un hueco, en anchos de producto.
    min_level_overlap: fraccion del alto (de la caja o del nivel, el
    menor) que una caja debe compartir con un nivel para cubrirlo.
    trim_to_products: acota la gondola a los productos (ver
    compute_availability)."""

    critical_free_fraction: float = CRITICAL_FREE_FRACTION
    min_gap_products: float = 1.0
    min_level_overlap: float = 0.3
    trim_to_products: bool = True

    def __post_init__(self) -> None:
        if not 0.0 < self.critical_free_fraction <= 1.0:
            raise ValueError("critical_free_fraction debe estar en (0, 1].")
        if self.min_gap_products < 0:
            raise ValueError("min_gap_products no puede ser negativo.")
        if not 0.0 < self.min_level_overlap <= 1.0:
            raise ValueError("min_level_overlap debe estar en (0, 1].")


@dataclass(frozen=True)
class ShelfAvailability:
    """Disponibilidad de un nivel de repisa. `level_index` es su posicion
    en los niveles de entrada; `bbox`, el nivel ya acotado a los
    productos. `gaps` son los tramos [x_inicio, x_fin] sin producto, de
    izquierda a derecha."""

    level_index: int
    bbox: BBox
    product_count: int
    gaps: tuple[Gap, ...]
    critical: bool

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    @property
    def free_width(self) -> float:
        return sum(end - start for start, end in self.gaps)

    @property
    def free_fraction(self) -> float:
        return self.free_width / self.width

    @property
    def occupied_fraction(self) -> float:
        return 1.0 - self.free_fraction

    @property
    def free_area_px(self) -> float:
        """Area frontal libre (Nivel 1): huecos por el alto del nivel."""
        return self.free_width * self.height


@dataclass(frozen=True)
class GondolaAvailability:
    """Disponibilidad de la gondola completa. `critical` es la alerta del
    MVP (Nivel 2); el detalle por repisa sirve para el Nivel 1."""

    shelves: tuple[ShelfAvailability, ...]
    free_fraction: float
    critical: bool

    @property
    def occupied_fraction(self) -> float:
        return 1.0 - self.free_fraction

    @property
    def critical_shelves(self) -> tuple[int, ...]:
        """`level_index` de las repisas con quiebre."""
        return tuple(shelf.level_index for shelf in self.shelves if shelf.critical)

    @property
    def free_area_px(self) -> float:
        return sum(shelf.free_area_px for shelf in self.shelves)


def compute_availability(
    products: Sequence[BBox] | np.ndarray,
    levels: Sequence[BBox] | np.ndarray,
    params: AvailabilityParams = AvailabilityParams(),
) -> GondolaAvailability:
    """Disponibilidad por repisa y de la gondola completa.

    `levels` son los bbox de cada nivel de repisa, de arriba hacia abajo
    (GondolaSegmentation.shelves). Si la segmentacion no encontro repisas
    (found=False), se pasa la ROI como unico nivel: analisis global.

    Con `trim_to_products` (por defecto), la gondola va del primer al
    ultimo nivel con productos y, a lo ancho, del producto mas a la
    izquierda al mas a la derecha. La ROI de la segmentacion suele
    incluir pasillo, techo o carteles, que sin esto cuentan como espacio
    vacio (en SKU-110K, 24% de falsas alertas con la gondola llena contra
    4%; ver scripts/evaluate_availability.py). Costo: una repisa extrema
    vacia por completo, o una franja vacia en todas las repisas en un
    extremo de la gondola, no se cuentan. Sin ningun producto no se acota
    y todo es hueco.
    """
    level_boxes = _as_boxes(levels, "levels")
    if len(level_boxes) == 0:
        raise ValueError("Se necesita al menos un nivel (o la ROI como unico nivel).")
    if np.any(level_boxes[:, 2] <= level_boxes[:, 0]) or np.any(
        level_boxes[:, 3] <= level_boxes[:, 1]
    ):
        raise ValueError("Cada nivel debe tener ancho y alto positivos.")
    boxes = _as_boxes(products, "products")
    boxes = boxes[(boxes[:, 2] > boxes[:, 0]) & (boxes[:, 3] > boxes[:, 1])]

    covering = [_covering_boxes(boxes, level, params.min_level_overlap) for level in level_boxes]
    stocked = [i for i, level_products in enumerate(covering) if len(level_products)]
    indices = range(len(level_boxes))
    if params.trim_to_products and stocked:
        indices = range(stocked[0], stocked[-1] + 1)
        in_gondola = np.concatenate([covering[i] for i in stocked])
        level_boxes = level_boxes.copy()
        level_boxes[:, 0] = np.maximum(level_boxes[:, 0], in_gondola[:, 0].min())
        level_boxes[:, 2] = np.minimum(level_boxes[:, 2], in_gondola[:, 2].max())
    # Ancho de producto de referencia para una repisa sin productos: la
    # mediana de toda la gondola. Sin ningun producto, todo es hueco.
    all_widths = boxes[:, 2] - boxes[:, 0]
    fallback_width = float(np.median(all_widths)) if len(all_widths) else 0.0

    shelves = []
    for index in indices:
        level = level_boxes[index]
        if level[2] <= level[0]:  # nivel fuera del ancho de los productos
            continue
        level_products = _covering_boxes(boxes, level, params.min_level_overlap)
        widths = level_products[:, 2] - level_products[:, 0]
        reference = float(np.median(widths)) if len(widths) else fallback_width
        gaps = _free_gaps(level, level_products, params.min_gap_products * reference)
        free = sum(end - start for start, end in gaps) / (level[2] - level[0])
        shelves.append(
            ShelfAvailability(
                level_index=index,
                bbox=tuple(float(v) for v in level),
                product_count=len(level_products),
                gaps=gaps,
                critical=free >= params.critical_free_fraction,
            )
        )

    total_width = sum(shelf.width for shelf in shelves)
    free_fraction = sum(shelf.free_width for shelf in shelves) / total_width
    return GondolaAvailability(
        shelves=tuple(shelves),
        free_fraction=free_fraction,
        critical=free_fraction >= params.critical_free_fraction,
    )


def free_volume_cm3(free_area_px: float, cm_per_px: float) -> float:
    """Volumen libre (Nivel 1) = area frontal libre x profundidad fija de
    25 cm. `cm_per_px` es la escala de la vista frontal, que depende de la
    camara (sin calibracion no hay escala: se informa el area en pixeles)."""
    if not cm_per_px > 0:
        raise ValueError("cm_per_px debe ser positivo.")
    return free_area_px * cm_per_px**2 * GONDOLA_DEPTH_CM


def _as_boxes(values: Sequence[BBox] | np.ndarray, name: str) -> np.ndarray:
    boxes = np.asarray(values, dtype=float).reshape(-1, 4) if len(values) else np.empty((0, 4))
    if not np.all(np.isfinite(boxes)):
        raise ValueError(f"{name} tiene coordenadas no finitas.")
    return boxes


def _covering_boxes(boxes: np.ndarray, level: np.ndarray, min_overlap: float) -> np.ndarray:
    """Cajas que ocupan el nivel: se cruzan con el en X y comparten con el
    al menos `min_overlap` del alto menor (el de la caja o el del nivel).
    Una caja puede cubrir dos niveles: si la segmentacion pone una repisa
    falsa a media altura de una fila de productos, ninguna de las dos
    mitades queda vacia."""
    overlap_y = np.minimum(boxes[:, 3], level[3]) - np.maximum(boxes[:, 1], level[1])
    heights = np.minimum(boxes[:, 3] - boxes[:, 1], level[3] - level[1])
    overlap_x = np.minimum(boxes[:, 2], level[2]) - np.maximum(boxes[:, 0], level[0])
    return boxes[(overlap_x > 0) & (overlap_y >= min_overlap * heights)]


def _free_gaps(level: np.ndarray, boxes: np.ndarray, min_width: float) -> tuple[Gap, ...]:
    """Tramos del nivel sin ninguna caja encima (union de las proyecciones
    en X), descartando los mas angostos que `min_width`."""
    left, right = float(level[0]), float(level[2])
    starts = np.clip(boxes[:, 0], left, right).tolist()
    ends = np.clip(boxes[:, 2], left, right).tolist()
    gaps = []
    cursor = left
    for x_min, x_max in sorted(zip(starts, ends)):
        if x_min > cursor:
            gaps.append((cursor, x_min))
        cursor = max(cursor, x_max)
    if cursor < right:
        gaps.append((cursor, right))
    return tuple((start, end) for start, end in gaps if end - start >= min_width)
