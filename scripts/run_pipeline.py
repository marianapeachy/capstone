"""CLI del pipeline ShelfVision AI (item #8): corre el pipeline completo
sobre fotos de gondola.

    python scripts/run_pipeline.py FOTOS_O_CARPETAS...
        [--weights data/processed/training/yolo26s/weights/best.pt]
        [--out data/processed/pipeline] [--device cpu] [--threads 4]
        [--conf 0.25] [--annotations ANOTACIONES.csv] [--iou 0.5]

Por foto escribe `<out>/<nombre>.jpg` (vista limpia: huecos, contorno de
las repisas medidas y cartel con la alerta y el % libre de la gondola) y
`<out>/<nombre>.json` (resultado completo, en coordenadas de la foto: la
alerta y el % libre son los de la gondola completa; por repisa, solo la
geometria). Imprime una tabla con el % libre y la alerta de cada gondola
y los segundos por etapa, con la mediana al final.

Evaluacion por lotes (CU07, RF06): con `--annotations` (CSV en el formato
estandar de data/processed/annotations/, filas con class_group "product")
compara las detecciones con la anotacion hecha a mano por IoU y la alerta
con la que da la misma anotacion medida por el pipeline, y escribe
`<out>/metrics.csv` (una fila por foto anotada y una fila "total"). Las
fotos se emparejan con la anotacion por nombre de archivo. Solo escribe
metricas: las imagenes no se copian a ningun otro lugar.

Codigo de salida 2 si faltan los pesos o no hay fotos.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.evaluation.detection_metrics import (  # noqa: E402
    IOU_THRESHOLD,
    DetectionMetrics,
    match_detections,
)
from src.pipeline import PipelineResult, measure_boxes, run_image  # noqa: E402
from src.reporting.annotate import draw_availability  # noqa: E402

DEFAULT_WEIGHTS = ROOT / "data" / "processed" / "training" / "yolo26s" / "weights" / "best.pt"
DEFAULT_OUT = ROOT / "data" / "processed" / "pipeline"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}
STAGES = ("correction", "segmentation", "detection", "availability", "total")
METRIC_FIELDS = [
    "image", "annotated", "detected", "true_positives", "false_positives", "false_negatives",
    "precision", "recall", "f1", "mean_iou", "free_fraction", "truth_free_fraction",
    "critical", "truth_critical", "alert_matches", "alert_accuracy", "free_mae",
]


def make_detector(weights: Path, device: str | None):
    """Carga YOLO26 una vez (import diferido: ultralytics tarda en cargar)."""
    from src.models.detector import ProductDetector

    return ProductDetector(weights, device=device)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Corre el pipeline completo sobre fotos de gondola.")
    parser.add_argument("inputs", nargs="+", type=Path, help="fotos y/o carpetas (no recursivo)")
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--device", default="cpu", help='"cpu", "0" (GPU), ...')
    parser.add_argument("--threads", type=int, default=4, help="hilos de PyTorch en CPU")
    parser.add_argument("--conf", type=float, default=None, help="confianza minima (por defecto, la del detector)")
    parser.add_argument("--annotations", type=Path, default=None,
                        help="CSV estandar con la anotacion hecha a mano (evaluacion por lotes)")
    parser.add_argument("--iou", type=float, default=IOU_THRESHOLD,
                        help="IoU minimo para emparejar una deteccion con la anotacion")
    return parser.parse_args(argv)


def find_images(inputs: list[Path]) -> list[Path]:
    images = []
    for path in inputs:
        if path.is_dir():
            images.extend(sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES))
        elif path.suffix.lower() in IMAGE_SUFFIXES:
            images.append(path)
    return images


def read_image(path: Path) -> np.ndarray | None:
    """cv2.imread no abre rutas con tildes en Windows: se lee como bytes."""
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
    except OSError:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None


def load_annotations(path: Path) -> dict[str, list[tuple[float, float, float, float]]]:
    """Cajas de producto por nombre de archivo de la foto."""
    boxes: dict[str, list] = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("class_group", "product") != "product":
                continue
            name = Path(row["image_path"].replace("\\", "/")).name
            boxes[name].append(tuple(float(row[k]) for k in ("x_min", "y_min", "x_max", "y_max")))
    return dict(boxes)


def evaluate(name: str, image: np.ndarray, result: PipelineResult, truth: list,
             iou_threshold: float) -> tuple[dict, DetectionMetrics]:
    reference = measure_boxes(image, truth)
    metrics = match_detections(result.products, truth, iou_threshold)
    row = {
        "image": name,
        "annotated": len(truth),
        "detected": len(result.products),
        "true_positives": metrics.true_positives,
        "false_positives": metrics.false_positives,
        "false_negatives": metrics.false_negatives,
        "precision": round(metrics.precision, 4),
        "recall": round(metrics.recall, 4),
        "f1": round(metrics.f1, 4),
        "mean_iou": round(metrics.mean_iou, 4),
        "free_fraction": round(result.free_fraction, 4),
        "truth_free_fraction": round(reference.free_fraction, 4),
        "critical": result.critical,
        "truth_critical": reference.critical,
        "alert_matches": result.critical == reference.critical,
    }
    return row, metrics


def total_row(rows: list[dict], metrics: list[DetectionMetrics]) -> dict:
    total = DetectionMetrics.total(metrics)
    return {
        "image": "total",
        "annotated": sum(r["annotated"] for r in rows),
        "detected": sum(r["detected"] for r in rows),
        "true_positives": total.true_positives,
        "false_positives": total.false_positives,
        "false_negatives": total.false_negatives,
        "precision": round(total.precision, 4),
        "recall": round(total.recall, 4),
        "f1": round(total.f1, 4),
        "mean_iou": round(total.mean_iou, 4),
        "alert_accuracy": round(sum(r["alert_matches"] for r in rows) / len(rows), 4),
        "free_mae": round(
            statistics.mean(abs(r["free_fraction"] - r["truth_free_fraction"]) for r in rows), 4
        ),
    }


def print_table(rows: list[tuple[str, PipelineResult | None, str]]) -> None:
    header = f"{'foto':<32} {'% libre':>8} {'alerta':>7}  " + " ".join(f"{s[:7]:>8}" for s in STAGES)
    print(header)
    print("-" * len(header))
    times = []
    for name, result, note in rows:
        if result is None:
            print(f"{name:<32} {note}")
            continue
        stage = [getattr(result.times, s) for s in STAGES]
        times.append(stage)
        alert = "SI" if result.critical else "no"
        print(f"{name:<32} {result.free_fraction:>8.0%} {alert:>7}  "
              + " ".join(f"{t:>8.2f}" for t in stage) + (f"  {note}" if note else ""))
    if times:
        medians = [statistics.median(column) for column in zip(*times)]
        print(f"{'mediana (s)':<32} {'':>8} {'':>7}  " + " ".join(f"{t:>8.2f}" for t in medians))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    images = find_images(args.inputs)
    if not images:
        print("No hay fotos (.jpg, .jpeg, .png o .bmp) en las rutas indicadas.", file=sys.stderr)
        return 2
    if not args.weights.exists():
        print(f"No existen los pesos {args.weights} (ver docs/training.md).", file=sys.stderr)
        return 2
    annotations = load_annotations(args.annotations) if args.annotations else {}

    started = time.perf_counter()
    if args.device == "cpu":
        import torch

        torch.set_num_threads(args.threads)
    detector = make_detector(args.weights, args.device)
    print(f"Modelo cargado en {time.perf_counter() - started:.1f} s ({args.weights.name}, {args.device}).")

    args.out.mkdir(parents=True, exist_ok=True)
    table, metric_rows, metrics = [], [], []
    for path in images:
        image = read_image(path)
        if image is None:
            table.append((path.name, None, "no se pudo leer"))
            continue
        result = run_image(image, detector, conf=args.conf)
        note = "" if result.segmentation_found else "sin repisas: analisis global"
        table.append((path.name, result, note))
        cv2.imencode(".jpg", draw_availability(image, result))[1].tofile(str(args.out / f"{path.stem}.jpg"))
        (args.out / f"{path.stem}.json").write_text(
            json.dumps(result.to_dict(), indent=2), encoding="utf-8"
        )
        if path.name in annotations:
            row, image_metrics = evaluate(path.name, image, result, annotations[path.name], args.iou)
            metric_rows.append(row)
            metrics.append(image_metrics)

    print_table(table)
    if args.annotations:
        if not metric_rows:
            print(f"Ninguna foto tiene anotacion en {args.annotations}.")
        else:
            total = total_row(metric_rows, metrics)
            with (args.out / "metrics.csv").open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=METRIC_FIELDS)
                writer.writeheader()
                writer.writerows([*metric_rows, total])
            print(f"\nEvaluacion contra la anotacion ({len(metric_rows)} fotos, IoU >= {args.iou}): "
                  f"P {total['precision']:.3f}  R {total['recall']:.3f}  F1 {total['f1']:.3f}  "
                  f"IoU medio {total['mean_iou']:.3f}  alerta correcta {total['alert_accuracy']:.0%}  "
                  f"error de % libre {total['free_mae']:.1%}")
    print(f"\nResultados en {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
