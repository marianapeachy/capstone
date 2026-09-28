"""Evaluacion de las repisas detectadas por segment_gondola() contra
repisas anotadas, como las de SHARD (altura Y de cada repisa como
fraccion del alto de la imagen, ver docs/datasets.md).

Cada ShelfLine detectada se reduce a una altura: su Y promedio entre
x_min y x_max, que en una recta es la Y en el centro del tramo (sirve
igual para repisas inclinadas). Las alturas detectadas y anotadas se
emparejan de a una (cada linea cuenta para una sola repisa) si difieren
en a lo mas `tolerance` (fraccion del alto): pares = TP, lineas sin par =
FP, repisas anotadas sin par = FN.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence

# Holgura para comparar fracciones con 2 decimales (las de SHARD) sin que
# el redondeo de punto flotante deje fuera un par justo en la tolerancia.
_EPS = 1e-9


class Line(Protocol):
    x_min: float
    x_max: float

    def y_at(self, x: float) -> float: ...


@dataclass(frozen=True)
class ShelfMatch:
    """Conteos de una imagen (o de varias, sumados con +)."""

    tp: int
    fp: int
    fn: int

    def __add__(self, other: ShelfMatch) -> ShelfMatch:
        return ShelfMatch(self.tp + other.tp, self.fp + other.fp, self.fn + other.fn)

    @property
    def precision(self) -> float:
        """TP / lineas detectadas; NaN si no se detecto ninguna."""
        return _ratio(self.tp, self.tp + self.fp)

    @property
    def recall(self) -> float:
        """TP / repisas anotadas; NaN si no hay repisas anotadas."""
        return _ratio(self.tp, self.tp + self.fn)

    @property
    def f1(self) -> float:
        """2 TP / (2 TP + FP + FN); NaN si no hay lineas ni repisas."""
        return _ratio(2 * self.tp, 2 * self.tp + self.fp + self.fn)


def line_height_fraction(line: Line, height: float) -> float:
    """Y promedio de la recta en su tramo, como fraccion del alto."""
    return line.y_at((line.x_min + line.x_max) / 2) / height


def match_shelf_heights(
    predicted: Iterable[float],
    expected: Iterable[float],
    tolerance: float,
    border_margin: float = 0.0,
) -> ShelfMatch:
    """Empareja alturas (fracciones del alto) de a una, con diferencia
    <= tolerance, maximizando la cantidad de pares.

    `border_margin` (fraccion del alto) deja fuera de la evaluacion las
    alturas detectadas y anotadas a menos de ese margen del borde superior
    o inferior: una repisa cortada por el borde de la foto no deja un salto
    de brillo que detectar.

    En una dimension basta recorrer ambas listas ordenadas: el menor de los
    dos valores en curso, si no alcanza al otro, no alcanza a ninguno de
    los que siguen y queda sin par.
    """
    predicted = sorted(_inside(predicted, border_margin))
    expected = sorted(_inside(expected, border_margin))
    i = j = tp = 0
    while i < len(predicted) and j < len(expected):
        if abs(predicted[i] - expected[j]) <= tolerance + _EPS:
            tp += 1
            i += 1
            j += 1
        elif predicted[i] < expected[j]:
            i += 1
        else:
            j += 1
    return ShelfMatch(tp=tp, fp=len(predicted) - tp, fn=len(expected) - tp)


def evaluate_shelf_lines(
    lines: Iterable[Line],
    height: float,
    expected: Sequence[float],
    tolerance: float,
    border_margin: float = 0.0,
) -> ShelfMatch:
    """Compara las ShelfLine de una imagen (de alto `height`) con las
    alturas anotadas (ver match_shelf_heights)."""
    predicted = [line_height_fraction(line, height) for line in lines]
    return match_shelf_heights(predicted, expected, tolerance, border_margin)


def summarize(matches: Sequence[ShelfMatch]) -> dict:
    """Totales de varias imagenes: precision, recall y F1 sobre los conteos
    sumados (micro) y F1 promedio por imagen (macro, sin las NaN)."""
    total = sum(matches, ShelfMatch(0, 0, 0))
    per_image = [m.f1 for m in matches if not math.isnan(m.f1)]
    return {
        "images": len(matches),
        "tp": total.tp,
        "fp": total.fp,
        "fn": total.fn,
        "precision": total.precision,
        "recall": total.recall,
        "f1": total.f1,
        "f1_per_image": sum(per_image) / len(per_image) if per_image else math.nan,
    }


def _inside(heights: Iterable[float], margin: float) -> list[float]:
    return [h for h in heights if margin <= h <= 1 - margin]


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else math.nan
