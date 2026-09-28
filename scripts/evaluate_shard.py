"""Mide las repisas de segment_gondola() contra las anotadas en SHARD
(altura de cada repisa como fraccion del alto, ver docs/datasets.md y
src/evaluation/shelf_evaluation.py): precision, recall y F1 de repisas,
por imagen y en total.

Requiere SHARD en data/raw/shard/ (python scripts/download_datasets.py
--dataset shard). Las fotos de SHARD no traen distorsion de lente: se
corrigen sin calibracion (solo CLAHE), como en visualize_segmentation.py.

Muestras fijas: las imagenes se barajan con --seed; "dev" son las
primeras --sample (para ajustar el metodo) y "holdout" las --sample
siguientes (para confirmar que un cambio no se sobreajusto a dev).

Salidas en data/processed/shard_eval/ (no versionado):
    <split>_seed<seed>.csv   alturas detectadas y anotadas + TP/FP/FN por imagen

Uso:
    python scripts/evaluate_shard.py                      # dev, 1000 imagenes, semilla 0
    python scripts/evaluate_shard.py --split holdout
    python scripts/evaluate_shard.py --tolerance 0.05 --border-margin 0.03
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.datasets.converters import parse_shard_shelf_coords  # noqa: E402
from src.evaluation.shelf_evaluation import (  # noqa: E402
    ShelfMatch,
    line_height_fraction,
    match_shelf_heights,
    summarize,
)
from src.preprocessing.gondola_segmentation import segment_gondola  # noqa: E402
from src.preprocessing.image_correction import correct_image  # noqa: E402

SHARD_DIR = ROOT / "data" / "raw" / "shard"
# El annotation.csv que viene dentro del .7z esta truncado: se usa el de
# figshare (ver src/datasets/sources.py).
ANNOTATIONS_CSV = SHARD_DIR / "annotation.csv"
IMAGES_DIR = SHARD_DIR / "shelf_detection"
OUTPUT_DIR = ROOT / "data" / "processed" / "shard_eval"

DEFAULT_TOLERANCE = 0.03  # del alto; SHARD separa repisas por ~0.12 (mediana)
REPORT_TOLERANCES = (0.02, 0.03, 0.05)


def load_annotations() -> pd.DataFrame:
    annotations = pd.read_csv(ANNOTATIONS_CSV, sep=";")
    # Dos imagenes aparecen repetidas con la misma anotacion.
    return annotations.drop_duplicates("filename").reset_index(drop=True)


def select(annotations: pd.DataFrame, split: str, sample: int, seed: int) -> pd.DataFrame:
    shuffled = annotations.sample(frac=1, random_state=seed).reset_index(drop=True)
    start = 0 if split == "dev" else sample
    return shuffled.iloc[start : start + sample]


def segment(filename: str) -> list[float]:
    """Alturas (fraccion del alto) de las repisas detectadas, ordenadas."""
    image = cv2.imread(str(IMAGES_DIR / filename))
    if image is None:
        raise FileNotFoundError(IMAGES_DIR / filename)
    height = image.shape[0]
    segmentation = segment_gondola(correct_image(image).image)
    return sorted(line_height_fraction(line, height) for line in segmentation.shelf_lines)


def score(results: pd.DataFrame, tolerance: float, border_margin: float) -> list[ShelfMatch]:
    return [
        match_shelf_heights(predicted, expected, tolerance, border_margin)
        for predicted, expected in zip(results["predicted"], results["expected"])
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--split", choices=["dev", "holdout"], default="dev")
    parser.add_argument("--sample", type=int, default=1000, help="imagenes por muestra (default 1000)")
    parser.add_argument("--seed", type=int, default=0, help="semilla del barajado (default 0)")
    parser.add_argument(
        "--tolerance", type=float, default=DEFAULT_TOLERANCE,
        help=f"diferencia maxima de altura, fraccion del alto (default {DEFAULT_TOLERANCE})",
    )
    parser.add_argument(
        "--border-margin", type=float, default=0.0,
        help="no evalua repisas ni lineas a menos de este margen del borde (default 0)",
    )
    parser.add_argument("--workers", type=int, default=None, help="procesos en paralelo")
    args = parser.parse_args()

    if not ANNOTATIONS_CSV.exists():
        sys.exit(f"No existe {ANNOTATIONS_CSV}: python scripts/download_datasets.py --dataset shard")
    chosen = select(load_annotations(), args.split, args.sample, args.seed)

    with ProcessPoolExecutor(args.workers) as pool:
        segmented = list(pool.map(segment, chosen["filename"], chunksize=8))
    results = pd.DataFrame(
        {
            "filename": chosen["filename"].to_numpy(),
            "predicted": segmented,
            "expected": [parse_shard_shelf_coords(c) for c in chosen["shelfCoord"]],
        }
    )

    matches = score(results, args.tolerance, args.border_margin)
    results = results.assign(
        tp=[m.tp for m in matches],
        fp=[m.fp for m in matches],
        fn=[m.fn for m in matches],
        f1=[m.f1 for m in matches],
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / f"{args.split}_seed{args.seed}.csv"
    results.assign(
        predicted=[",".join(f"{h:.4f}" for h in p) for p in results["predicted"]],
        expected=[",".join(f"{h:.2f}" for h in e) for e in results["expected"]],
    ).to_csv(out, index=False)

    print(f"SHARD {args.split} ({len(results)} imagenes, semilla {args.seed}, "
          f"margen de borde {args.border_margin})")
    rows = []
    for tolerance in sorted({args.tolerance, *REPORT_TOLERANCES}):
        summary = summarize(score(results, tolerance, args.border_margin))
        rows.append({"tolerancia": tolerance, **summary})
    table = pd.DataFrame(rows).set_index("tolerancia")
    print(table.round(3).to_string())
    print(f"\nlineas por imagen: {results['predicted'].map(len).mean():.2f} "
          f"(anotadas: {results['expected'].map(len).mean():.2f})")
    print(f"Detalle por imagen en {out}")


if __name__ == "__main__":
    main()
