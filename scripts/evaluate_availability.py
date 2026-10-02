"""Mide el criterio de quiebre de stock (src/postprocessing/availability.py)
sin detector entrenado: las anotaciones hacen de detector perfecto y se
simulan sus fallas y los quiebres.

Las gondolas de SKU-110K y de Kaggle estan en su mayoria llenas, asi que
sirven para medir falsas alertas y cuanto quiebre hace falta para que la
alerta salte:

- recall: cada producto se descarta con probabilidad 1 - recall (un
  producto no detectado parece un hueco).
- quiebre: se quitan los productos cuyo centro cae en una franja vertical
  al azar de esa fraccion del ancho, en todas las repisas. "interior":
  la franja cae dentro de los productos, lejos de sus extremos;
  "cualquiera": en cualquier parte de la ROI, incluidos los extremos.

Variantes de niveles de repisa (columnas de las tablas):

- segmentacion: los niveles de segment_gondola() (rectangulos
  horizontales), con la gondola acotada a los productos.
- roi: los mismos, sin acotar (la ROI completa de la segmentacion).
- hibrido: shelf_levels() (item #22), franjas inclinadas entre las filas
  de productos y las repisas de la segmentacion. Se calcula con los
  productos "detectados" de cada escenario, como en el pipeline.

Vistas en angulo (--yaw, --pitch): cada foto se gira con oblique_view()
(src/datasets/synthetic.py) junto con sus anotaciones, para simular una
camara de sala. Solo con fotos que se pueden modificar (Kaggle, CC0):
la licencia de SKU-110K prohibe crear obras derivadas de sus fotos.

Cada imagen se corrige sin calibracion (solo CLAHE, los datasets no traen
distorsion de lente) y se segmenta con segment_gondola(); sin repisas, la
ROI es el unico nivel. En SKU-110K se usa el split "val" (el "test" se
reserva para evaluar el detector, ver docs/training.md); Kaggle no tiene
splits (45 fotos).

Salida en data/processed/availability_eval/ (no versionado):
    <dataset>_<split>_seed<seed>.csv   espacio libre por imagen, vista,
                                       escenario y variante

Uso:
    python scripts/evaluate_availability.py                 # SKU-110K val, 300 imagenes
    python scripts/evaluate_availability.py --dataset kaggle --yaw 0 20 35 --pitch -15
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import astuple, dataclass
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.datasets.synthetic import oblique_view  # noqa: E402
from src.postprocessing.availability import (  # noqa: E402
    CRITICAL_FREE_FRACTION,
    AvailabilityParams,
    compute_availability,
)
from src.postprocessing.shelf_levels import shelf_levels  # noqa: E402
from src.preprocessing.gondola_segmentation import segment_gondola  # noqa: E402
from src.preprocessing.image_correction import correct_image  # noqa: E402

ANNOTATIONS_DIR = ROOT / "data" / "processed" / "annotations"
OUTPUT_DIR = ROOT / "data" / "processed" / "availability_eval"


@dataclass(frozen=True)
class Dataset:
    annotations: Path
    images: Path
    splits: bool  # si False, se usan todas las fotos
    modifiable: bool  # su licencia permite modificar las fotos (vistas en angulo)


DATASETS = {
    "sku110k": Dataset(
        ANNOTATIONS_DIR / "sku110k.csv",
        ROOT / "data" / "raw" / "sku-110k" / "SKU110K_fixed",
        splits=True,
        modifiable=False,
    ),
    "kaggle": Dataset(
        ANNOTATIONS_DIR / "kaggle_supermarket.csv",
        ROOT / "data" / "raw" / "supermarket-shelves" / "Supermarket shelves",
        splits=False,
        modifiable=True,
    ),
}

RECALLS = (1.0, 0.9, 0.8)
STOCKOUTS = (0.2, 0.3, 0.4)
THRESHOLDS = (0.2, 0.25, 0.3, 0.35, 0.4)
TRIM, NO_TRIM = AvailabilityParams(), AvailabilityParams(trim_to_products=False)
# Margen de la franja "interior" respecto de los extremos de los productos.
INTERIOR_MARGIN = 0.05


def segment(task: tuple[Path, np.ndarray, float, float]) -> dict:
    """Gira la foto (si corresponde) y la segmenta. Devuelve los productos
    anotados en la vista, los niveles horizontales, las repisas y la ROI."""
    image_path, boxes, yaw, pitch = task
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(image_path)
    if yaw or pitch:
        image, boxes = oblique_view(image, boxes, yaw, pitch)
    segmentation = segment_gondola(correct_image(image).image)
    return {
        "boxes": boxes,
        "levels": np.asarray(segmentation.shelves or (segmentation.roi,), dtype=float),
        "lines": [astuple(line) for line in segmentation.shelf_lines],
        "roi": segmentation.roi,
    }


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
    products: np.ndarray, roi: tuple[int, int, int, int], rng: np.random.Generator
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
                        remove_band(detected, roi[0], roi[2], fraction, rng)))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dataset", choices=sorted(DATASETS), default="sku110k")
    parser.add_argument("--split", choices=["train", "val", "test"], default="val",
                        help="split de SKU-110K (Kaggle no tiene)")
    parser.add_argument("--sample", type=int, default=300, help="imagenes (default 300)")
    parser.add_argument("--seed", type=int, default=0, help="semilla (default 0)")
    parser.add_argument("--yaw", type=float, nargs="+", default=[0.0],
                        help="giros de la camara hacia el lado, en grados (default 0)")
    parser.add_argument("--pitch", type=float, default=0.0,
                        help="giro hacia abajo de las vistas con yaw != 0 (default 0)")
    parser.add_argument("--workers", type=int, default=4, help="procesos en paralelo (default 4)")
    args = parser.parse_args()

    dataset = DATASETS[args.dataset]
    views = [(yaw, args.pitch if yaw else 0.0) for yaw in args.yaw]
    if not dataset.modifiable and any(yaw or pitch for yaw, pitch in views):
        sys.exit(f"La licencia de {args.dataset} no permite modificar sus fotos: sin --yaw/--pitch.")
    if not dataset.annotations.exists():
        sys.exit(f"No existe {dataset.annotations}: python scripts/prepare_datasets.py")
    annotations = pd.read_csv(dataset.annotations)
    if "class_group" in annotations:
        annotations = annotations[annotations["class_group"] == "product"]
    split = args.split if dataset.splits else "all"
    if dataset.splits:
        annotations = annotations[annotations["split"] == split]
    paths = pd.Series(annotations["image_path"].unique())
    paths = paths.sample(n=min(args.sample, len(paths)), random_state=args.seed).tolist()
    boxes = {
        path: group[["x_min", "y_min", "x_max", "y_max"]].to_numpy(dtype=float)
        for path, group in annotations[annotations["image_path"].isin(paths)].groupby("image_path")
    }
    tasks = [(dataset.images / path, boxes[path], yaw, pitch) for yaw, pitch in views for path in paths]

    with ProcessPoolExecutor(args.workers) as pool:
        segmented = list(pool.map(segment, tasks, chunksize=4))

    rng = np.random.default_rng(args.seed)
    rows = []
    for (image_path, _, yaw, pitch), view in zip(tasks, segmented):
        view_name = f"yaw {yaw:g} pitch {pitch:g}"
        for recall, scenario, products in scenarios(view["boxes"], view["roi"], rng):
            results = {
                "segmentacion": compute_availability(products, view["levels"], TRIM),
                "roi": compute_availability(products, view["levels"], NO_TRIM),
                "hibrido": compute_availability(
                    products, shelf_levels(products, view["lines"], view["roi"]), TRIM
                ),
            }
            for variant, result in results.items():
                rows.append(
                    {
                        "image_path": str(image_path.relative_to(dataset.images)),
                        "view": view_name,
                        "recall": recall,
                        "scenario": scenario,
                        "variant": variant,
                        "free_fraction": result.free_fraction,
                    }
                )
    results = pd.DataFrame(rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_DIR / f"{args.dataset}_{split}_seed{args.seed}.csv", index=False)

    print(f"{args.dataset} {split} ({len(paths)} imagenes, semilla {args.seed})")
    alerts = results.assign(alert=results["free_fraction"] >= CRITICAL_FREE_FRACTION)
    print(f"\nImagenes con alerta (libre >= {CRITICAL_FREE_FRACTION:.0%}), por vista y recall simulado:")
    table = alerts.pivot_table(
        index=["view", "recall", "scenario"], columns="variant", values="alert", aggfunc="mean"
    )
    print(table.round(3).to_string())

    print("\nFalsas alertas con la gondola llena, segun umbral:")
    full = results[results["scenario"] == "lleno"]
    rows = {
        (view, recall, variant): {f"{t:.0%}": (group["free_fraction"] >= t).mean() for t in THRESHOLDS}
        for (view, recall, variant), group in full.groupby(["view", "recall", "variant"])
    }
    print(pd.DataFrame.from_dict(rows, orient="index").round(3).to_string())


if __name__ == "__main__":
    main()
