"""Metricas de deteccion por IoU contra una anotacion hecha a mano.

Es como medira Walmart el sistema (reunion del 2026-09-16, README,
"Estrategia de Datos y Evaluacion"): cada caja anotada se empareja con a
lo mas una deteccion, la de mayor IoU, si supera el umbral. Las cajas van
en el formato estandar [x_min, y_min, x_max, y_max].
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

BBox = tuple[float, float, float, float]

IOU_THRESHOLD = 0.5


def iou(a: BBox, b: BBox) -> float:
    """Interseccion sobre union de dos cajas."""
    width = min(a[2], b[2]) - max(a[0], b[0])
    height = min(a[3], b[3]) - max(a[1], b[1])
    if width <= 0 or height <= 0:
        return 0.0
    inter = width * height
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union


@dataclass(frozen=True)
class DetectionMetrics:
    """Conteos de una imagen (o de varias, con `total`). `iou_sum` suma el
    IoU de cada emparejamiento, para promediarlo entre imagenes."""

    true_positives: int
    false_positives: int
    false_negatives: int
    iou_sum: float

    @property
    def precision(self) -> float:
        found = self.true_positives + self.false_positives
        return self.true_positives / found if found else 0.0

    @property
    def recall(self) -> float:
        annotated = self.true_positives + self.false_negatives
        return self.true_positives / annotated if annotated else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0

    @property
    def mean_iou(self) -> float:
        """IoU medio de los emparejamientos (verdaderos positivos)."""
        return self.iou_sum / self.true_positives if self.true_positives else 0.0

    @staticmethod
    def total(metrics: Iterable[DetectionMetrics]) -> DetectionMetrics:
        metrics = list(metrics)
        return DetectionMetrics(
            true_positives=sum(m.true_positives for m in metrics),
            false_positives=sum(m.false_positives for m in metrics),
            false_negatives=sum(m.false_negatives for m in metrics),
            iou_sum=sum(m.iou_sum for m in metrics),
        )


def match_detections(
    predicted: Sequence[BBox], truth: Sequence[BBox], iou_threshold: float = IOU_THRESHOLD
) -> DetectionMetrics:
    """Empareja detecciones y anotaciones de una imagen, de a pares, de
    mayor a menor IoU (greedy): cada una se usa una sola vez."""
    pairs = sorted(
        (
            (overlap, p, t)
            for p, box in enumerate(predicted)
            for t, annotated in enumerate(truth)
            if (overlap := iou(box, annotated)) >= iou_threshold
        ),
        reverse=True,
    )
    used_predicted, used_truth, iou_sum = set(), set(), 0.0
    for overlap, p, t in pairs:
        if p in used_predicted or t in used_truth:
            continue
        used_predicted.add(p)
        used_truth.add(t)
        iou_sum += overlap
    matched = len(used_truth)
    return DetectionMetrics(
        true_positives=matched,
        false_positives=len(predicted) - matched,
        false_negatives=len(truth) - matched,
        iou_sum=iou_sum,
    )
