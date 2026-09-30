"""Mide el criterio de quiebre de stock (src/postprocessing/availability.py)
sobre SKU-110K, sin detector entrenado: las anotaciones hacen de detector
perfecto y se simulan sus fallas y los quiebres.

SKU-110K son en su mayoria gondolas llenas, asi que sirve para medir
falsas alertas y cuanto quiebre hace falta para que la alerta salte:

- recall: cada producto se descarta con probabilidad 1 - recall (un
  producto no detectado parece un hueco).
- quiebre: se quitan los productos cuyo centro cae en una franja vertical
  al azar de esa fraccion del ancho, en todas las repisas. "interior":
  la franja cae dentro de los productos, lejos de sus extremos;
  "cualquiera": en cualquier parte de la ROI, incluidos los extremos.

Se compara la gondola acotada a los productos (por defecto) con la ROI
completa de la segmentacion (--no-trim en la tabla: "roi").

Cada imagen se corrige sin calibracion (solo CLAHE, SKU-110K no trae
distorsion de lente) y se segmenta con segment_gondola(); sin repisas, la
ROI es el unico nivel. Se usa el split "val" (el "test" se reserva para
evaluar el detector, ver docs/training.md).

Salida en data/processed/availability_eval/ (no versionado):
    <split>_seed<seed>.csv   espacio libre por imagen, escenario y variante

Uso:
    python scripts/evaluate_availability.py                 # val, 300 imagenes, semilla 0
    python scripts/evaluate_availability.py --sample 588 --workers 4
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.postprocessing.availability import (  # noqa: E402
    CRITICAL_FREE_FRACTION,
    AvailabilityParams,
    compute_availability,
)
from src.preprocessing.gondola_segmentation import segment_gondola  # noqa: E402
from src.preprocessing.image_correction import correct_image  # noqa: E402

ANNOTATIONS_CSV = ROOT / "data" / "processed" / "annotations" / "sku110k.csv"
IMAGES_ROOT = ROOT / "data" / "raw" / "sku-110k" / "SKU110K_fixed"
OUTPUT_DIR = ROOT / "data" / "processed" / "availability_eval"

RECALLS = (1.0, 0.9, 0.8)
STOCKOUTS = (0.2, 0.3, 0.4)
THRESHOLDS = (0.2, 0.25, 0.3, 0.35, 0.4)
VARIANTS = {"productos": AvailabilityParams(), "roi": AvailabilityParams(trim_to_products=False)}
# Margen de la franja "interior" respecto de los extremos de los productos.
INTERIOR_MARGIN = 0.05


def segment(image_path: str) -> tuple[tuple[int, int, int, int], ...]:
    """Niveles de repisa de la imagen (o la ROI si no hay repisas)."""
    image = cv2.imread(str(IMAGES_ROOT / image_path))
    if image is None:
        raise FileNotFoundError(IMAGES_ROOT / image_path)
    segmentation = segment_gondola(correct_image(image).image)
    return segmentation.shelves or (segmentation.roi,)


def remove_band(
    products: np.ndarray, left: float, right: float, fraction: float, rng: np.random.Generator
) -> np.ndarray:
    """Quita los productos con el centro en una franja al azar de
    `fraction` del ancho [left, right]."""
    band = fraction * (right - left)
    start = rng.uniform(left, right - band)
    centers = (products[:, 0] + products[:, 2]) / 2
    return products[(centers < start) | (centers > start + band)]


def scenarios(
    products: np.ndarray, levels: np.ndarray, rng: np.random.Generator
) -> list[tuple[float, str, np.ndarray]]:
    """(recall, escenario, productos) de una imagen."""
    out = []
    for recall in RECALLS:
        detected = products[rng.random(len(products)) < recall] if recall < 1.0 else products
        out.append((recall, "lleno", detected))
        if len(detected) == 0:
            continue
        x_min, x_max = detected[:, 0].min(), detected[:, 2].max()
        margin = INTERIOR_MARGIN * (x_max - x_min)
        for fraction in STOCKOUTS:
            out.append((recall, f"quiebre {fraction:.0%} interior",
                        remove_band(detected, x_min + margin, x_max - margin, fraction, rng)))
            out.append((recall, f"quiebre {fraction:.0%} cualquiera",
                        remove_band(detected, levels[:, 0].min(), levels[:, 2].max(), fraction, rng)))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--split", choices=["train", "val", "test"], default="val")
    parser.add_argument("--sample", type=int, default=300, help="imagenes (default 300)")
    parser.add_argument("--seed", type=int, default=0, help="semilla (default 0)")
    parser.add_argument("--workers", type=int, default=None, help="procesos en paralelo")
    args = parser.parse_args()

    if not ANNOTATIONS_CSV.exists():
        sys.exit(f"No existe {ANNOTATIONS_CSV}: python scripts/prepare_datasets.py --dataset sku110k")
    annotations = pd.read_csv(ANNOTATIONS_CSV)
    annotations = annotations[annotations["split"] == args.split]
    paths = pd.Series(annotations["image_path"].unique())
    paths = paths.sample(n=min(args.sample, len(paths)), random_state=args.seed).tolist()
    boxes = {
        path: group[["x_min", "y_min", "x_max", "y_max"]].to_numpy(dtype=float)
        for path, group in annotations[annotations["image_path"].isin(paths)].groupby("image_path")
    }

    with ProcessPoolExecutor(args.workers) as pool:
        segmented = list(pool.map(segment, paths, chunksize=4))

    rng = np.random.default_rng(args.seed)
    rows = []
    for path, levels in zip(paths, segmented):
        levels = np.asarray(levels, dtype=float)
        for recall, scenario, products in scenarios(boxes[path], levels, rng):
            for variant, params in VARIANTS.items():
                result = compute_availability(products, levels, params)
                rows.append(
                    {
                        "image_path": path,
                        "recall": recall,
                        "scenario": scenario,
                        "variant": variant,
                        "free_fraction": result.free_fraction,
                    }
                )
    results = pd.DataFrame(rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_DIR / f"{args.split}_seed{args.seed}.csv", index=False)

    print(f"SKU-110K {args.split} ({len(paths)} imagenes, semilla {args.seed})")
    alerts = results.assign(alert=results["free_fraction"] >= CRITICAL_FREE_FRACTION)
    print(f"\nImagenes con alerta (libre >= {CRITICAL_FREE_FRACTION:.0%}), por recall simulado:")
    table = alerts.pivot_table(
        index=["recall", "scenario"], columns="variant", values="alert", aggfunc="mean"
    )
    print(table.round(3).to_string())

    print("\nFalsas alertas con la gondola llena, segun umbral:")
    full = results[results["scenario"] == "lleno"]
    rows = {
        (recall, variant): {f"{t:.0%}": (group["free_fraction"] >= t).mean() for t in THRESHOLDS}
        for (recall, variant), group in full.groupby(["recall", "variant"])
    }
    print(pd.DataFrame.from_dict(rows, orient="index").round(3).to_string())


if __name__ == "__main__":
    main()
