"""Visor de la segmentacion automatica de gondola sobre imagenes de los
datasets: corre correct_image() + segment_gondola() y dibuja la ROI, los
bordes de repisa y las anotaciones del dataset, junto con las metricas
aproximadas de src/evaluation/segmentation_proxy.py.

Con --dataset shard dibuja ademas las repisas anotadas en SHARD (verde) y
las metricas de src/evaluation/shelf_evaluation.py (TP/FP/FN y F1 de
repisas; para medir sobre muestras grandes, scripts/evaluate_shard.py).

Requiere haber corrido antes scripts/prepare_datasets.py (o, para SHARD,
scripts/download_datasets.py --dataset shard). Los datasets
publicos no traen distorsion de lente, asi que se corrige sin calibracion
(solo CLAHE) y las coordenadas corregidas coinciden con las originales.

Salidas en data/processed/segmentation_preview/ (no versionado):
    sheet_<dataset>.jpg   una lamina por dataset para revisar a ojo
    metrics.csv           metricas por imagen

Uso:
    python scripts/visualize_segmentation.py
    python scripts/visualize_segmentation.py --dataset sku110k --per-dataset 12 --seed 3
    python scripts/visualize_segmentation.py --per-dataset 0 --metrics-sample 200
    python scripts/visualize_segmentation.py --dataset shard --per-dataset 12 --seed 3
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.datasets.converters import parse_shard_shelf_coords  # noqa: E402
from src.evaluation.segmentation_proxy import (  # noqa: E402
    area_fraction,
    centers_inside_fraction,
    resting_on_lines_fraction,
    supported_lines_fraction,
)
from src.evaluation.shelf_evaluation import ShelfMatch, evaluate_shelf_lines, summarize  # noqa: E402
from src.preprocessing.gondola_segmentation import segment_gondola  # noqa: E402
from src.preprocessing.image_correction import correct_image  # noqa: E402

ANNOTATIONS_CSV = ROOT / "data" / "processed" / "annotations" / "all_annotations.csv"
OUTPUT_DIR = ROOT / "data" / "processed" / "segmentation_preview"

# Carpeta a la que es relativo image_path en all_annotations.csv (ver
# scripts/prepare_datasets.py).
DATASET_ROOTS = {
    "sku110k": ROOT / "data" / "raw" / "sku-110k" / "SKU110K_fixed",
    "kaggle_supermarket": ROOT / "data" / "raw" / "supermarket-shelves" / "Supermarket shelves",
    "unidatapro": ROOT / "data" / "raw" / "grocery-shelves-unidatapro",
    "roboflow_out_of_stock": ROOT / "data" / "raw" / "out-of-stock-detection-roboflow",
    "roboflow_empty_shelf": ROOT / "data" / "raw" / "empty-shelf-detector-roboflow",
}

SHARD = "shard"
SHARD_DIR = ROOT / "data" / "raw" / "shard"

# Tolerancia para "producto apoyado en una repisa", relativa al alto.
RESTING_TOLERANCE = 0.025
# Diferencia maxima de altura con una repisa de SHARD (igual que
# scripts/evaluate_shard.py).
SHARD_TOLERANCE = 0.03

TILE_HEIGHT = 480
SHEET_COLUMNS = 3
BOX_COLORS = {"product": (160, 160, 160), "empty_space": (0, 140, 255), "price": (255, 200, 0)}
ROI_COLOR = (0, 200, 0)
LINE_COLOR = (0, 0, 255)
EXPECTED_LINE_COLOR = (0, 220, 0)


def evaluate(dataset: str, image_path: str, boxes: pd.DataFrame) -> tuple[dict, np.ndarray | None]:
    image = cv2.imread(str(DATASET_ROOTS[dataset] / image_path))
    if image is None:
        return {"dataset": dataset, "image_path": image_path, "error": "no se pudo leer"}, None
    height, width = image.shape[:2]
    corrected = correct_image(image)
    segmentation = segment_gondola(corrected.image)

    xyxy = boxes[["x_min", "y_min", "x_max", "y_max"]].to_numpy(dtype=float)
    products = boxes.loc[
        boxes["class_group"] == "product", ["x_min", "y_min", "x_max", "y_max"]
    ].to_numpy(dtype=float)
    tolerance = RESTING_TOLERANCE * height
    metrics = {
        "dataset": dataset,
        "image_path": image_path,
        "found": segmentation.found,
        "shelves": len(segmentation.shelves),
        "annotations_inside_roi": centers_inside_fraction(segmentation.roi, xyxy),
        "roi_area_fraction": area_fraction(segmentation.roi, width, height),
        "products_on_shelf_line": resting_on_lines_fraction(
            segmentation.shelf_lines, products, tolerance
        ),
        "shelf_lines_with_products": (
            supported_lines_fraction(segmentation.shelf_lines, products, tolerance)
            if len(products)
            else math.nan
        ),
    }
    caption = (
        f"{image_path[-28:]}  "
        + ("OK" if metrics["found"] else "SIN REPISAS")
        + f"  niveles={metrics['shelves']}"
        + f"  dentro={_fmt(metrics['annotations_inside_roi'])}"
        + f"  area={_fmt(metrics['roi_area_fraction'])}"
        + f"  apoyados={_fmt(metrics['products_on_shelf_line'])}"
    )
    return metrics, draw(corrected.image, segmentation, boxes, caption)


def evaluate_shard(image_path: str, expected: tuple[float, ...]) -> tuple[dict, np.ndarray | None]:
    image = cv2.imread(str(SHARD_DIR / "shelf_detection" / image_path))
    if image is None:
        return {"dataset": SHARD, "image_path": image_path, "error": "no se pudo leer"}, None
    height, width = image.shape[:2]
    corrected = correct_image(image)
    segmentation = segment_gondola(corrected.image)
    match = evaluate_shelf_lines(segmentation.shelf_lines, height, expected, SHARD_TOLERANCE)
    metrics = {
        "dataset": SHARD,
        "image_path": image_path,
        "found": segmentation.found,
        "shelves": len(segmentation.shelves),
        "roi_area_fraction": area_fraction(segmentation.roi, width, height),
        "tp": match.tp,
        "fp": match.fp,
        "fn": match.fn,
        "shelf_f1": match.f1,
    }
    canvas = corrected.image.copy()
    thickness = max(1, round(max(canvas.shape[:2]) / 600))
    for y in expected:
        cv2.line(canvas, (0, round(y * height)), (width, round(y * height)), EXPECTED_LINE_COLOR, thickness * 2)
    caption = (
        f"{image_path[:13]}  TP={match.tp} FP={match.fp} FN={match.fn}  F1={_fmt(match.f1)}"
        f"  area={_fmt(metrics['roi_area_fraction'])}"
    )
    return metrics, draw(canvas, segmentation, pd.DataFrame(columns=["class_group"]), caption)


def draw(image: np.ndarray, segmentation, boxes: pd.DataFrame, caption: str) -> np.ndarray:
    canvas = image.copy()
    thickness = max(1, round(max(canvas.shape[:2]) / 600))
    for row in boxes.itertuples():
        color = BOX_COLORS.get(row.class_group, (200, 200, 200))
        cv2.rectangle(
            canvas, (int(row.x_min), int(row.y_min)), (int(row.x_max), int(row.y_max)), color, thickness
        )
    for index, line in enumerate(segmentation.shelf_lines):
        start = (int(line.x_min), int(round(line.y_at(line.x_min))))
        end = (int(line.x_max), int(round(line.y_at(line.x_max))))
        cv2.line(canvas, start, end, LINE_COLOR, thickness * 3)
    x_min, y_min, x_max, y_max = segmentation.roi
    cv2.rectangle(canvas, (x_min, y_min), (x_max - 1, y_max - 1), ROI_COLOR, thickness * 4)
    for level, (_, top, _, bottom) in enumerate(segmentation.shelves, start=1):
        cv2.putText(
            canvas, f"N{level}", (x_min + 8 * thickness, (top + bottom) // 2),
            cv2.FONT_HERSHEY_SIMPLEX, thickness * 0.9, ROI_COLOR, thickness * 2,
        )

    scale = TILE_HEIGHT / canvas.shape[0]
    tile = cv2.resize(canvas, (max(1, round(canvas.shape[1] * scale)), TILE_HEIGHT))
    header = np.full((28, tile.shape[1], 3), 255, dtype=np.uint8)
    cv2.putText(header, caption, (6, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    return np.vstack([header, tile])


def _fmt(value: float) -> str:
    return "-" if value is None or math.isnan(value) else f"{value:.2f}"


def contact_sheet(tiles: list[np.ndarray]) -> np.ndarray:
    tile_width = max(t.shape[1] for t in tiles)
    padded = [
        cv2.copyMakeBorder(t, 0, 0, 0, tile_width - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255))
        for t in tiles
    ]
    padded += [np.full_like(padded[0], 255)] * (-len(padded) % SHEET_COLUMNS)
    rows = [np.hstack(padded[i : i + SHEET_COLUMNS]) for i in range(0, len(padded), SHEET_COLUMNS)]
    return np.vstack(rows)


def review_shard(args: argparse.Namespace) -> list[dict]:
    """Lamina y metricas de repisas sobre una muestra de SHARD."""
    csv_path = SHARD_DIR / "annotation.csv"
    if not csv_path.exists():
        sys.exit(f"No existe {csv_path}: python scripts/download_datasets.py --dataset shard")
    annotations = pd.read_csv(csv_path, sep=";").drop_duplicates("filename")
    sample = annotations.sample(
        n=min(len(annotations), args.per_dataset + args.metrics_sample), random_state=args.seed
    )
    rows, tiles = [], []
    for index, row in enumerate(sample.itertuples()):
        expected = parse_shard_shelf_coords(row.shelfCoord)
        metrics, tile = evaluate_shard(row.filename, expected)
        rows.append(metrics)
        if tile is not None and index < args.per_dataset:
            tiles.append(tile)
    if tiles:
        cv2.imwrite(str(OUTPUT_DIR / f"sheet_{SHARD}.jpg"), contact_sheet(tiles))
    total = summarize([ShelfMatch(r["tp"], r["fp"], r["fn"]) for r in rows if "tp" in r])
    print(
        f"{SHARD}: {total['images']} imagenes  precision={_fmt(total['precision'])}"
        f"  recall={_fmt(total['recall'])}  F1={_fmt(total['f1'])}"
        f"  (verde: anotadas, rojo: detectadas)"
    )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", choices=[*sorted(DATASET_ROOTS), SHARD], action="append",
                        help="dataset a revisar (repetible; por defecto todos menos shard)")
    parser.add_argument("--per-dataset", type=int, default=9, help="imagenes por lamina (default 9)")
    parser.add_argument("--metrics-sample", type=int, default=0,
                        help="imagenes extra por dataset solo para metricas, sin dibujar")
    parser.add_argument("--seed", type=int, default=0, help="semilla del muestreo")
    args = parser.parse_args()

    datasets = args.dataset or sorted(DATASET_ROOTS)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    if SHARD in datasets:
        rows += review_shard(args)
    datasets = [d for d in datasets if d != SHARD]
    if datasets and not ANNOTATIONS_CSV.exists():
        sys.exit(f"No existe {ANNOTATIONS_CSV}: correr antes scripts/prepare_datasets.py")
    annotations = pd.read_csv(ANNOTATIONS_CSV) if datasets else pd.DataFrame()

    for dataset in datasets:
        subset = annotations[annotations["dataset"] == dataset]
        paths = subset["image_path"].drop_duplicates()
        sample = paths.sample(
            n=min(len(paths), args.per_dataset + args.metrics_sample), random_state=args.seed
        ).tolist()
        by_image = subset[subset["image_path"].isin(sample)].groupby("image_path")
        tiles = []
        for index, image_path in enumerate(sample):
            metrics, tile = evaluate(dataset, image_path, by_image.get_group(image_path))
            rows.append(metrics)
            if tile is not None and index < args.per_dataset:
                tiles.append(tile)
        if tiles:
            cv2.imwrite(str(OUTPUT_DIR / f"sheet_{dataset}.jpg"), contact_sheet(tiles))

    results = pd.DataFrame(rows)
    results.to_csv(OUTPUT_DIR / "metrics.csv", index=False)
    results = results[results["dataset"] != SHARD]
    if results.empty:
        print(f"\nLaminas y metrics.csv en {OUTPUT_DIR}")
        return
    summary = results.groupby("dataset").agg(
        imagenes=("image_path", "count"),
        con_repisas=("found", "mean"),
        niveles=("shelves", "mean"),
        dentro_roi=("annotations_inside_roi", "mean"),
        area_roi=("roi_area_fraction", "mean"),
        apoyados=("products_on_shelf_line", "mean"),
        repisas_con_productos=("shelf_lines_with_products", "mean"),
    )
    print(summary.round(2).to_string())
    print(f"\nLaminas y metrics.csv en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
