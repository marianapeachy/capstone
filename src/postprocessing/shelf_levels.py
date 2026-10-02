"""Niveles de repisa desde los productos detectados y las repisas de la
segmentacion (item #22 de PROGRESS.md).

Con la camara en angulo (foto oblicua o camara de sala), segment_gondola()
pierde repisas: acepta poca inclinacion y en vista oblicua cada repisa da
varios bordes (superficie, borde frontal, sombra). El detector, en
cambio, sigue encontrando los productos, y los productos de una repisa se
apoyan en ella: sus bases quedan alineadas en una recta, aunque este
inclinada. Este modulo combina ambas fuentes:

1. Filas de productos: rectas que pasan por las bases de al menos
   `min_row_products` productos (busqueda tipo Hough sobre la pendiente,
   luego ajuste por minimos cuadrados). No son repisas: una recta que
   cruza por la mitad de los productos (diagonal entre filas distintas);
   una capa de una pila, cuyos productos se apoyan directo sobre otros
   productos, sin el borde de una repisa entre medio (quedan en el nivel
   de la repisa de abajo: la altura de las pilas no se mide); y una fila
   cuya pendiente no calza con la de las demas. Las repisas son paralelas
   en la gondola, asi que en la foto convergen a un mismo punto de fuga y
   la pendiente de cada una varia en linea recta con su altura.
2. Repisas de la segmentacion: aportan las repisas vacias, que no tienen
   productos que las marquen. Se descartan las que cruzan por la mitad de
   los productos (falsa repisa sobre una fila de productos iguales, item
   #17), las que cruzan una repisa ya aceptada y las que quedan cerca de
   una fila de productos: menos de `min_shelf_spacing` de la distancia
   tipica entre filas. Esas son otro borde de la misma repisa (la tira de
   precios bajo los productos) y crearian un nivel delgado y vacio; una
   repisa vacia de verdad es tan alta como las demas.
3. Niveles: franjas inclinadas entre dos repisas consecutivas, como
   cuadrilateros de lados verticales que compute_availability() acepta.
   Sobre la primera repisa se agrega un nivel, del alto de los productos
   que se apoyan en ella. Bajo la ultima no: los productos ahi no forman
   una fila (si la formaran, habria otra repisa) y suelen ser los que la
   foto corta en su borde inferior; como nivel, parecerian una repisa casi
   vacia. Costo: una ultima repisa con menos de `min_row_products`
   productos y sin borde visible para la segmentacion no se mide.
   Cada nivel se acota al tramo donde su linea central queda dentro de
   la ROI: con la camara en angulo, una repisa puede salir de la foto por
   arriba o por abajo, y ahi no hay productos que detectar.
   Se descartan los niveles sin productos mas bajos que `min_empty_level`
   veces el alto mediano de los niveles con productos: son el borde de una
   repisa (la tira de precios), no una repisa vacia, que es tan alta como
   las demas.

Todo llega como tuplas (no importa src/preprocessing ni src/models): las
repisas, como (x_min, x_max, pendiente, intercepto) de y = m * x + b, que
es dataclasses.astuple() de una ShelfLine de la segmentacion; los
productos, como [x_min, y_min, x_max, y_max]. Mismo sistema de
coordenadas para ambos: el de la imagen corregida.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

BBox = tuple[float, float, float, float]
Line = tuple[float, float, float, float]
Point = tuple[float, float]
Quad = tuple[Point, Point, Point, Point]


@dataclass(frozen=True)
class ShelfLevelParams:
    """Las distancias van en altos de producto (la mediana de la gondola),
    para no depender de la resolucion ni de la distancia a la camara.

    row_tolerance: desvio maximo de una base respecto de la recta de su
    fila. max_tilt_deg: inclinacion maxima de una fila. min_row_products:
    productos minimos de una fila. crossing_margin: una recta cruza un
    producto si pasa a mas de esta fraccion de su alto de sus bordes
    superior e inferior. min_separation: distancia minima entre dos
    repisas (mas cerca, son la misma). stack_gap: un producto esta
    apilado si su base queda a menos de esta distancia del tope del
    producto de abajo; max_stacked: fraccion de productos apilados desde
    la que una fila es la capa de una pila. vanishing_tolerance_deg:
    desvio maximo de la pendiente de una fila respecto del modelo de
    punto de fuga de la gondola. min_shelf_spacing: distancia minima de
    una repisa de la segmentacion a una fila de productos, en fraccion de
    la distancia mediana entre filas consecutivas. min_empty_level: alto
    minimo de un nivel sin productos, en fraccion del alto mediano de los
    niveles con productos."""

    row_tolerance: float = 0.15
    max_tilt_deg: float = 35.0
    tilt_step_deg: float = 0.5
    min_row_products: int = 3
    crossing_margin: float = 0.25
    min_separation: float = 0.5
    stack_gap: float = 0.15
    max_stacked: float = 0.5
    vanishing_tolerance_deg: float = 3.0
    min_shelf_spacing: float = 0.4
    min_empty_level: float = 0.5

    def __post_init__(self) -> None:
        if not self.row_tolerance > 0:
            raise ValueError("row_tolerance debe ser positivo.")
        if not 0 < self.max_tilt_deg < 90:
            raise ValueError("max_tilt_deg debe estar en (0, 90).")
        if not self.tilt_step_deg > 0:
            raise ValueError("tilt_step_deg debe ser positivo.")
        if self.min_row_products < 2:
            raise ValueError("min_row_products debe ser al menos 2.")
        if not 0 <= self.crossing_margin < 0.5:
            raise ValueError("crossing_margin debe estar en [0, 0.5).")
        if self.min_separation < 0:
            raise ValueError("min_separation no puede ser negativo.")
        if not 0 < self.max_stacked <= 1:
            raise ValueError("max_stacked debe estar en (0, 1].")
        if not 0 <= self.min_empty_level < 1:
            raise ValueError("min_empty_level debe estar en [0, 1).")
        if not 0 <= self.min_shelf_spacing < 1:
            raise ValueError("min_shelf_spacing debe estar en [0, 1).")
        if not self.vanishing_tolerance_deg > 0:
            raise ValueError("vanishing_tolerance_deg debe ser positivo.")


def product_rows(
    products: Sequence[BBox] | np.ndarray, params: ShelfLevelParams = ShelfLevelParams()
) -> list[Line]:
    """Repisas marcadas por filas de productos (rectas por sus bases), de
    la mas poblada a la menos poblada. Cada producto pertenece a lo mas a
    una fila."""
    boxes = _valid_boxes(products)
    if len(boxes) < params.min_row_products:
        return []
    xs = (boxes[:, 0] + boxes[:, 2]) / 2
    ys = boxes[:, 3]
    heights = boxes[:, 3] - boxes[:, 1]
    tolerance = params.row_tolerance * float(np.median(heights))
    tilt = np.arange(-params.max_tilt_deg, params.max_tilt_deg + 1e-9, params.tilt_step_deg)
    slopes = np.tan(np.radians(tilt))
    max_slope = math.tan(math.radians(params.max_tilt_deg))

    unit = float(np.median(heights))
    rows: list[Line] = []
    weights: list[int] = []
    remaining = np.ones(len(boxes), dtype=bool)
    while remaining.sum() >= params.min_row_products:
        row = _best_row(boxes, xs, ys, remaining, slopes, max_slope, tolerance, params)
        if row is None:
            break
        line, members = row
        remaining &= ~members
        if _stacked_fraction(boxes, members, unit, params) > params.max_stacked:
            continue
        rows.append(line)
        weights.append(int(members.sum()))
    return _consistent_rows(rows, weights, unit, params)


def shelf_lines(
    products: Sequence[BBox] | np.ndarray,
    segmentation_lines: Sequence[Line],
    x_range: tuple[float, float],
    params: ShelfLevelParams = ShelfLevelParams(),
) -> list[Line]:
    """Repisas de la gondola, de arriba hacia abajo: las filas de
    productos y las repisas de la segmentacion que no las contradicen.
    Ninguna cruza a otra ni queda a menos de `min_separation` dentro de
    `x_range` (x_min, x_max), el ancho donde se usaran como limites de
    nivel."""
    boxes = _valid_boxes(products)
    unit = float(np.median(boxes[:, 3] - boxes[:, 1])) if len(boxes) else 0.0
    center = (x_range[0] + x_range[1]) / 2
    accepted: list[Line] = []
    for line in product_rows(boxes, params):
        if _compatible(line, accepted, x_range, params.min_separation * unit):
            accepted.append(line)
    rows = sorted(_y_at(line, center) for line in accepted)
    spacing = float(np.median(np.diff(rows))) if len(rows) > 1 else 0.0
    rows_only = list(accepted)
    for line in segmentation_lines:
        line = _as_line(line)
        if len(boxes) and _crosses_products(line, boxes, unit, params):
            continue
        if not _compatible(line, rows_only, x_range, params.min_shelf_spacing * spacing):
            continue
        if _compatible(line, accepted, x_range, params.min_separation * unit):
            accepted.append(line)
    return sorted(accepted, key=lambda line: _y_at(line, center))


def shelf_levels(
    products: Sequence[BBox] | np.ndarray,
    segmentation_lines: Sequence[Line],
    roi: BBox,
    params: ShelfLevelParams = ShelfLevelParams(),
) -> tuple[Quad, ...]:
    """Niveles de repisa como cuadrilateros (sup. izq., sup. der., inf.
    der., inf. izq.) de lados verticales, de arriba hacia abajo, a lo
    ancho de la ROI. Sin ninguna repisa, la ROI es el unico nivel
    (analisis global)."""
    x_min, y_min, x_max, y_max = (float(v) for v in roi)
    if not (x_max > x_min and y_max > y_min):
        raise ValueError("La ROI debe tener ancho y alto positivos.")
    boxes = _valid_boxes(products)
    lines = shelf_lines(boxes, segmentation_lines, (x_min, x_max), params)
    if not lines:
        flat_top, flat_bottom = (x_min, x_max, 0.0, y_min), (x_min, x_max, 0.0, y_max)
        return (_quad(flat_top, flat_bottom, x_min, x_max),)

    bounds = list(lines)
    first = lines[0]
    xs = (boxes[:, 0] + boxes[:, 2]) / 2
    above = boxes[_above(first, boxes, xs)] if len(boxes) else boxes
    if len(above):
        # Nivel superior: hasta el tope del producto mas alto sobre la
        # primera repisa.
        lift = float(np.max(_y_at(first, (above[:, 0] + above[:, 2]) / 2) - above[:, 1]))
        bounds.insert(0, _shift(first, -lift))
    levels = []
    for top, bottom in zip(bounds, bounds[1:]):
        visible = _visible_range(top, bottom, (x_min, y_min, x_max, y_max))
        if visible is not None:
            levels.append(_quad(top, bottom, *visible))
    return _drop_thin_empty_levels(levels, boxes, params)


def _visible_range(top: Line, bottom: Line, roi: BBox) -> tuple[float, float] | None:
    """Tramo [x0, x1] de la ROI donde la linea central del nivel queda
    dentro de la ROI en vertical (None si no queda dentro en ninguna parte)."""
    x_min, y_min, x_max, y_max = roi
    slope = (top[2] + bottom[2]) / 2
    intercept = (top[3] + bottom[3]) / 2
    if abs(slope) < 1e-12:
        inside = y_min <= intercept <= y_max
        return (x_min, x_max) if inside else None
    ends = sorted(((y_min - intercept) / slope, (y_max - intercept) / slope))
    x0, x1 = max(x_min, ends[0]), min(x_max, ends[1])
    return (x0, x1) if x1 > x0 else None


def _drop_thin_empty_levels(
    levels: list[Quad], boxes: np.ndarray, params: ShelfLevelParams
) -> tuple[Quad, ...]:
    """Quita los niveles sin ningun centro de producto dentro y mas bajos
    que min_empty_level del alto mediano de los niveles con productos."""
    if not len(boxes) or len(levels) < 2:
        return tuple(levels)
    xs = (boxes[:, 0] + boxes[:, 2]) / 2
    ys = (boxes[:, 1] + boxes[:, 3]) / 2
    heights, stocked = [], []
    for (x0, top0), (x1, top1), (_, bottom1), (_, bottom0) in levels:
        t = (np.clip(xs, x0, x1) - x0) / (x1 - x0)
        inside = (xs >= x0) & (xs <= x1) & (ys > top0 + t * (top1 - top0)) & (ys < bottom0 + t * (bottom1 - bottom0))
        heights.append(((bottom0 - top0) + (bottom1 - top1)) / 2)
        stocked.append(bool(inside.any()))
    if not any(stocked):
        return tuple(levels)
    reference = float(np.median([h for h, s in zip(heights, stocked) if s]))
    return tuple(
        level
        for level, height, has_products in zip(levels, heights, stocked)
        if has_products or height >= params.min_empty_level * reference
    )


def _above(line: Line, boxes: np.ndarray, xs: np.ndarray) -> np.ndarray:
    """Productos con el centro sobre la recta."""
    return (boxes[:, 1] + boxes[:, 3]) / 2 < _y_at(line, xs)


def _best_row(
    boxes: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    remaining: np.ndarray,
    slopes: np.ndarray,
    max_slope: float,
    tolerance: float,
    params: ShelfLevelParams,
) -> tuple[Line, np.ndarray] | None:
    """La fila con mas bases alineadas entre los productos que quedan.
    Por cada pendiente, la ventana de interceptos de ancho 2*tolerancia
    con mas bases; se prueban de la mas poblada a la menos poblada hasta
    una que no cruce productos."""
    index = np.flatnonzero(remaining)
    candidates = []
    for slope in slopes:
        intercepts = np.sort(ys[index] - slope * xs[index])
        counts = np.searchsorted(intercepts, intercepts + 2 * tolerance, side="right") - np.arange(
            len(intercepts)
        )
        best = int(np.argmax(counts))
        candidates.append((int(counts[best]), float(slope), float(intercepts[best] + tolerance)))
    candidates.sort(key=lambda c: (-c[0], abs(c[1])))
    unit = float(np.median(boxes[:, 3] - boxes[:, 1]))
    for count, slope, intercept in candidates:
        if count < params.min_row_products:
            return None
        members = remaining & (np.abs(ys - (slope * xs + intercept)) <= tolerance)
        # Una fila son productos lado a lado (no apilados en la misma X).
        if members.sum() < params.min_row_products or np.ptp(xs[members]) == 0:
            continue
        # Ajuste fino por minimos cuadrados sobre las bases de la fila.
        slope, intercept = np.polyfit(xs[members], ys[members], 1)
        slope = float(np.clip(slope, -max_slope, max_slope))
        intercept = float(np.mean(ys[members] - slope * xs[members]))
        members = remaining & (np.abs(ys - (slope * xs + intercept)) <= tolerance)
        if members.sum() < params.min_row_products:
            continue
        line = (
            float(boxes[members, 0].min()),
            float(boxes[members, 2].max()),
            slope,
            intercept,
        )
        if not _crosses_products(line, boxes, unit, params):
            return line, members
    return None


def _stacked_fraction(
    boxes: np.ndarray, members: np.ndarray, unit: float, params: ShelfLevelParams
) -> float:
    """Fraccion de los productos de la fila apoyados directo sobre otro
    producto: uno debajo, que comparte al menos la mitad del ancho menor,
    con el tope a menos de stack_gap de su base (o encimado, cuando las
    cajas de dos productos se solapan)."""
    widths = boxes[:, 2] - boxes[:, 0]
    heights = boxes[:, 3] - boxes[:, 1]
    centers = (boxes[:, 1] + boxes[:, 3]) / 2
    stacked = 0
    index = np.flatnonzero(members)
    for j in index:
        overlap_x = np.minimum(boxes[:, 2], boxes[j, 2]) - np.maximum(boxes[:, 0], boxes[j, 0])
        gap = boxes[:, 1] - boxes[j, 3]
        below = (
            (centers > centers[j])
            & (overlap_x >= 0.5 * np.minimum(widths, widths[j]))
            & (gap <= params.stack_gap * unit)
            & (gap >= -0.5 * np.minimum(heights, heights[j]))
        )
        stacked += bool(below.any())
    return stacked / len(index) if len(index) else 0.0


def _consistent_rows(
    rows: list[Line], weights: list[int], unit: float, params: ShelfLevelParams
) -> list[Line]:
    """Las filas que calzan con un mismo punto de fuga: pendiente lineal
    en la altura de la fila (en una foto de frente, todas horizontales).
    Se prueba el modelo de cada par de filas y el de pendiente constante,
    y gana el que suma mas productos en sus filas."""
    if len(rows) < 3:
        return rows
    x_ref = float(np.mean([(line[0] + line[1]) / 2 for line in rows]))
    angles = np.degrees(np.arctan([line[2] for line in rows]))
    heights = np.array([line[2] * x_ref + line[3] for line in rows])
    slopes = np.array([line[2] for line in rows])
    weight = np.array(weights, dtype=float)
    models = [(0.0, float(np.median(slopes)))]
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if abs(heights[j] - heights[i]) >= unit:
                a = (slopes[j] - slopes[i]) / (heights[j] - heights[i])
                models.append((a, slopes[i] - a * heights[i]))
    best, best_weight = None, -1.0
    for a, c in models:
        predicted = np.degrees(np.arctan(a * heights + c))
        inliers = np.abs(angles - predicted) <= params.vanishing_tolerance_deg
        if weight[inliers].sum() > best_weight:
            best, best_weight = inliers, float(weight[inliers].sum())
    return [line for line, keep in zip(rows, best) if keep]


def _crosses_products(
    line: Line, boxes: np.ndarray, unit: float, params: ShelfLevelParams
) -> bool:
    """La recta pasa por la mitad de mas productos de los que se apoyan en
    ella (y por al menos 2): es una fila de productos o una diagonal
    entre filas, no una repisa."""
    xs = (boxes[:, 0] + boxes[:, 2]) / 2
    inside = (xs >= line[0]) & (xs <= line[1])
    y = _y_at(line, xs)
    heights = boxes[:, 3] - boxes[:, 1]
    crossed = (
        inside
        & (y > boxes[:, 1] + params.crossing_margin * heights)
        & (y < boxes[:, 3] - params.crossing_margin * heights)
    )
    resting = inside & (np.abs(boxes[:, 3] - y) <= max(params.row_tolerance, 0.25) * unit)
    return int(crossed.sum()) >= 2 and crossed.sum() > resting.sum()


def _compatible(
    line: Line, accepted: list[Line], x_range: tuple[float, float], min_distance: float
) -> bool:
    """No cruza ni queda a menos de min_distance de ninguna repisa
    aceptada, dentro de x_range."""
    for other in accepted:
        gaps = [_y_at(line, x) - _y_at(other, x) for x in x_range]
        if gaps[0] * gaps[1] <= 0 or min(abs(g) for g in gaps) < max(min_distance, 1e-6):
            return False
    return True


def _valid_boxes(products: Sequence[BBox] | np.ndarray) -> np.ndarray:
    boxes = np.asarray(products, dtype=float).reshape(-1, 4) if len(products) else np.empty((0, 4))
    if not np.all(np.isfinite(boxes)):
        raise ValueError("products tiene coordenadas no finitas.")
    return boxes[(boxes[:, 2] > boxes[:, 0]) & (boxes[:, 3] > boxes[:, 1])]


def _as_line(line: Sequence[float]) -> Line:
    values = tuple(float(v) for v in line)
    if len(values) != 4 or not all(math.isfinite(v) for v in values):
        raise ValueError("Cada repisa es (x_min, x_max, pendiente, intercepto) finitos.")
    return values  # type: ignore[return-value]


def _y_at(line: Line, x: float | np.ndarray) -> float | np.ndarray:
    return line[2] * x + line[3]


def _shift(line: Line, dy: float) -> Line:
    return (line[0], line[1], line[2], line[3] + dy)


def _quad(top: Line, bottom: Line, x_min: float, x_max: float) -> Quad:
    """Nivel entre dos rectas, a lo ancho de [x_min, x_max]."""
    return (
        (x_min, float(_y_at(top, x_min))),
        (x_max, float(_y_at(top, x_max))),
        (x_max, float(_y_at(bottom, x_max))),
        (x_min, float(_y_at(bottom, x_min))),
    )
