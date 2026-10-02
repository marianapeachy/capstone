"""Fine-tuning y evaluacion de YOLO26 sobre SKU-110K (item #5 de PROGRESS.md).

Entrena y valida en el mismo modo en que infiere el pipeline
(src/models/detector.py): cabeza sin NMS (nms=False) y max_det=1000. Por
defecto Ultralytics valida con NMS externo y, durante el entrenamiento,
corta en 300 cajas por imagen; asi, las metricas y la eleccion de best.pt
medirian un modelo distinto del que se usa. Las corridas quedan en
data/processed/training/<nombre>/ (weights/best.pt, weights/last.pt).

Uso (en un PC con GPU NVIDIA; ver docs/training.md):
    python scripts/train_detector.py train --variant yolo26s
    python scripts/train_detector.py train --variant yolo26s-p2
    python scripts/train_detector.py resume data/processed/training/yolo26s
    python scripts/train_detector.py resume data/processed/training/yolo26s-p2 --batch 1
    python scripts/train_detector.py val --weights data/processed/training/yolo26s/weights/best.pt

Prueba corta en CPU (verifica el flujo, no entrena en serio):
    python scripts/train_detector.py train --variant yolo26n --data data/processed/yolo/sku110k-limit16/data.yaml \\
        --device cpu --imgsz 320 --epochs 1 --batch 2 --workers 0 --name smoke
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO  # noqa: E402

from src.models.detector import IMGSZ, MAX_DET  # noqa: E402
from src.models.power import disable_eco_qos  # noqa: E402
from src.models.vram import limit_vram  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "data" / "processed" / "yolo" / "sku110k" / "data.yaml"
RUNS_DIR = ROOT / "data" / "processed" / "training"

# variante -> (arquitectura o pesos iniciales, pesos COCO a transferir).
# La variante P2 agrega una cabeza para objetos chicos: se construye desde
# su YAML y hereda de yolo26s.pt las capas que coinciden.
VARIANTS = {
    "yolo26n": ("yolo26n.pt", None),
    "yolo26s": ("yolo26s.pt", None),
    "yolo26s-p2": ("yolo26s-p2.yaml", "yolo26s.pt"),
}


def require_cuda(device: str) -> None:
    if device == "cpu":
        return
    import torch

    if not torch.cuda.is_available():
        sys.exit(
            f"PyTorch {torch.__version__} no ve ninguna GPU CUDA. Instala PyTorch con CUDA "
            "(ver docs/training.md) o usa --device cpu solo para una prueba corta."
        )


def prepare_process(device: str, reserve_gib: float) -> None:
    # Sin esto, en Windows un pico de memoria pagina a la RAM compartida en
    # vez de fallar, y la epoca sigue ~18 veces mas lenta (ver src/models/vram.py).
    if reserve_gib > 0 and (summary := limit_vram(device, reserve_gib)):
        print(summary)
    # Lanzado en segundo plano, Windows lo mandaria a los nucleos de eficiencia.
    if disable_eco_qos():
        print("EcoQoS de Windows desactivado para este proceso")


def build_model(variant: str) -> YOLO:
    source, transfer = VARIANTS[variant]
    model = YOLO(source)
    if transfer:
        model.load(transfer)
    return model


def train(args: argparse.Namespace) -> None:
    require_cuda(args.device)
    prepare_process(args.device, args.vram_reserve)
    build_model(args.variant).train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        patience=args.patience,
        project=str(RUNS_DIR),
        name=args.name or args.variant,
        nms=False,
        max_det=MAX_DET,
        seed=0,
    )


def resume(args: argparse.Namespace) -> None:
    run = Path(args.run)
    last = run if run.suffix == ".pt" else run / "weights" / "last.pt"
    if not last.exists():
        sys.exit(f"No existe {last}")
    overrides = {"device": args.device} if args.device else {}
    if args.batch:
        overrides["batch"] = args.batch
    require_cuda(args.device or "0")
    prepare_process(args.device or "0", args.vram_reserve)
    YOLO(str(last)).train(resume=True, **overrides)


def val(args: argparse.Namespace) -> None:
    require_cuda(args.device)
    disable_eco_qos()
    # Absoluta: Ultralytics anida un `project` relativo dentro de runs/detect/.
    weights = Path(args.weights).resolve()
    run_dir = weights.parent.parent
    metrics = YOLO(str(weights)).val(
        data=str(args.data),
        split=args.split,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        nms=False,
        max_det=MAX_DET,
        project=str(run_dir),
        name=f"val-{args.split}",
        exist_ok=True,
    )
    summary = {
        "weights": weights.as_posix(),
        "split": args.split,
        "imgsz": args.imgsz,
        "precision": metrics.box.mp,
        "recall": metrics.box.mr,
        "map50": metrics.box.map50,
        "map75": metrics.box.map75,
        "map50_95": metrics.box.map,
    }
    out = run_dir / f"val-{args.split}" / "metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"metricas guardadas en {out.as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--data", type=Path, default=DEFAULT_DATA, help="data.yaml de scripts/prepare_yolo_dataset.py")
    common.add_argument("--imgsz", type=int, default=IMGSZ)
    common.add_argument("--device", default="0", help='GPU ("0", "0,1") o "cpu"')
    common.add_argument("--workers", type=int, default=8)
    vram = argparse.ArgumentParser(add_help=False)
    vram.add_argument(
        "--vram-reserve", type=float, default=1.5, help="GiB de la GPU que PyTorch deja libres (0: sin limite)"
    )

    p_train = sub.add_parser("train", parents=[common, vram], help="entrenar una variante")
    p_train.add_argument("--variant", choices=VARIANTS, required=True)
    p_train.add_argument("--epochs", type=int, default=50)
    p_train.add_argument("--batch", type=int, default=-1, help="-1: el mayor que quepa en ~60%% de la GPU")
    p_train.add_argument("--patience", type=int, default=15, help="epocas sin mejora antes de parar")
    p_train.add_argument("--name", help="nombre de la corrida (default: la variante)")
    p_train.set_defaults(func=train)

    p_resume = sub.add_parser("resume", parents=[vram], help="continuar una corrida cortada")
    p_resume.add_argument("run", help="carpeta de la corrida o su weights/last.pt")
    p_resume.add_argument("--device", help="cambiar el dispositivo guardado en la corrida")
    p_resume.add_argument("--batch", type=int, help="cambiar el batch guardado (ej. 1 si no cabe en la GPU)")
    p_resume.set_defaults(func=resume)

    p_val = sub.add_parser("val", parents=[common], help="evaluar pesos entrenados")
    p_val.add_argument("--weights", required=True)
    p_val.add_argument("--split", choices=("val", "test"), default="val")
    p_val.add_argument("--batch", type=int, default=8)
    p_val.set_defaults(func=val)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
