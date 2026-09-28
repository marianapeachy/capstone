"""Conversores de anotaciones de datasets externos al formato estandar
del proyecto: bounding box absoluto [x_min, y_min, x_max, y_max] (ver CLAUDE.md).

Cada dataset descargado en data/raw/ trae su propio formato de anotacion
(XML tipo CVAT, JSON tipo Supervisely, COCO JSON o CSV). Las funciones de
este modulo son puras (no tocan el sistema de archivos) para poder
probarlas con datos de ejemplo; la lectura de archivos vive en
scripts/prepare_datasets.py.
"""

from __future__ import annotations

BBox = tuple[float, float, float, float]

# Mapeo de clase original -> categoria generica usada por postprocessing
# (RF03: calculo de disponibilidad). "other" cubre clases que no aportan
# a la deteccion de producto ni de espacio vacio (ej. etiquetas de precio).
CLASS_GROUP_MAP: dict[str, dict[str, str]] = {
    "unidatapro": {"Box": "product"},
    "kaggle_supermarket": {"Product": "product", "Price": "price"},
    "sku110k": {"object": "product"},
    "roboflow_out_of_stock": {"empty": "empty_space"},
    "roboflow_empty_shelf": {
        "100% O.O.S": "empty_space",
        "100- O.O.S": "empty_space",
    },
}


def class_group(dataset_key: str, class_name: str) -> str:
    return CLASS_GROUP_MAP.get(dataset_key, {}).get(class_name, "other")


def clip_bbox(bbox: BBox, width: float, height: float) -> BBox:
    """Recorta un bbox a los limites [0, width] x [0, height] y ordena
    min/max, por si la fuente trae coordenadas invertidas o fuera de rango."""
    x_min, y_min, x_max, y_max = bbox
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    x_min = max(0.0, min(x_min, width))
    x_max = max(0.0, min(x_max, width))
    y_min = max(0.0, min(y_min, height))
    y_max = max(0.0, min(y_max, height))
    return x_min, y_min, x_max, y_max


def polyline_to_bbox(points: str) -> BBox:
    """Convierte el atributo `points` de un <polyline> estilo CVAT
    ("x1,y1;x2,y2;...") en el bbox que lo contiene."""
    xs: list[float] = []
    ys: list[float] = []
    for pair in points.strip().split(";"):
        x_str, y_str = pair.split(",")
        xs.append(float(x_str))
        ys.append(float(y_str))
    return min(xs), min(ys), max(xs), max(ys)


def coco_bbox_to_xyxy(bbox: list[float]) -> BBox:
    """COCO guarda [x, y, width, height] en pixeles absolutos desde la
    esquina superior izquierda; lo pasamos a [x_min, y_min, x_max, y_max]."""
    x, y, w, h = bbox
    return x, y, x + w, y + h


def supervisely_rect_to_xyxy(exterior: list[list[float]]) -> BBox:
    """Supervisely (formato del dataset de Kaggle) guarda un rectangulo
    como dos puntos [[x1, y1], [x2, y2]] sin garantizar orden top-left/
    bottom-right."""
    xs = [p[0] for p in exterior]
    ys = [p[1] for p in exterior]
    return min(xs), min(ys), max(xs), max(ys)


def sku110k_row_to_bbox(x1: float, y1: float, x2: float, y2: float) -> BBox:
    """SKU-110K ya publica sus anotaciones como
    [x_min, y_min, x_max, y_max] absolutos; esta funcion solo normaliza
    el orden/tipos para mantener la misma interfaz que los demas
    conversores."""
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def parse_shard_shelf_coords(text: str) -> tuple[float, ...]:
    """Alturas de repisa de una fila de annotation.csv de SHARD (columna
    shelfCoord: fracciones del alto separadas por coma, en cualquier
    orden), ordenadas de arriba hacia abajo. SHARD no anota bboxes: estas
    alturas evaluan la segmentacion (src/evaluation/shelf_evaluation.py)."""
    values = tuple(sorted(float(v) for v in text.split(",") if v.strip()))
    if any(not 0.0 <= v <= 1.0 for v in values):
        raise ValueError(f"altura de repisa fuera de [0, 1]: {text!r}")
    return values
