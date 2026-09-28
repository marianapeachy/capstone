"""CLI de descarga reproducible de los datasets publicos del proyecto a
data/raw/ (catalogo en src/datasets/sources.py, detalle en
docs/datasets.md). Despues de descargar, correr
scripts/prepare_datasets.py para convertir las anotaciones.

Uso:
    python scripts/download_datasets.py --list     # catalogo y licencias
    python scripts/download_datasets.py --check    # verifica data/raw/ sin descargar
    python scripts/download_datasets.py            # descarga los que falten
    python scripts/download_datasets.py --dataset sku110k
    python scripts/download_datasets.py --force    # vuelve a descargar

Los datasets de Roboflow necesitan una API key (gratis, en
https://app.roboflow.com/settings/api) en la variable de entorno
ROBOFLOW_API_KEY o en el archivo .env. Sin ella se omiten.

Un dataset que ya esta completo en data/raw/ no se vuelve a descargar,
asi que tambien sirve para verificar datasets copiados a mano (por ejemplo,
un .zip compartido por otro integrante). Las descargas grandes se
reanudan si se cortan: el archivo parcial queda en data/raw/.downloads/.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import py7zr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.datasets.sources import (  # noqa: E402
    DATASETS,
    HUGGINGFACE_SKIP,
    DatasetSource,
    check_layout,
    huggingface_file_url,
    huggingface_revision_url,
    roboflow_export_url,
    safe_destination,
    strip_archive_root,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DOWNLOADS = DATA_RAW / ".downloads"

USER_AGENT = "shelfvision-ai-dataset-downloader"
CHUNK_SIZE = 1 << 20  # 1 MiB
PROGRESS_MIN_BYTES = 50_000_000  # bajo esto, una sola linea por archivo


def fetch_json(url: str) -> dict:
    with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=60) as resp:
        return json.load(resp)


def download_file(url: str, dest: Path, expected_size: int | None = None) -> Path:
    """Descarga `url` a `dest`, reanudando un `.part` previo si el
    servidor lo permite. Si se conoce `expected_size`, un tamano distinto
    se trata como descarga incompleta."""
    if dest.exists() and (expected_size is None or dest.stat().st_size == expected_size):
        print(f"  ya descargado: {dest.name}")
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    start = part.stat().st_size if part.exists() else 0
    headers = {"User-Agent": USER_AGENT}
    if start:
        headers["Range"] = f"bytes={start}-"

    with urlopen(Request(url, headers=headers), timeout=60) as resp:
        if start and resp.status != 206:
            start = 0  # el servidor no permite reanudar: se parte de cero
        length = resp.headers.get("Content-Length")
        total = start + int(length) if length else None
        done = start
        next_report = 0.0
        with part.open("ab" if start else "wb") as f:
            while chunk := resp.read(CHUNK_SIZE):
                f.write(chunk)
                done += len(chunk)
                if total and total >= PROGRESS_MIN_BYTES and done / total >= next_report:
                    print(f"  {dest.name}: {done / 1e6:,.0f} / {total / 1e6:,.0f} MB")
                    next_report += 0.1

    size = part.stat().st_size
    if not total or total < PROGRESS_MIN_BYTES:
        print(f"  descargado: {dest.name} ({size / 1e6:,.1f} MB)")
    if expected_size is not None and size != expected_size:
        raise RuntimeError(
            f"{dest.name}: se descargaron {size} bytes, se esperaban {expected_size}. "
            "Vuelve a correr el script para reanudar."
        )
    part.replace(dest)
    return dest


def extract_archive(archive: Path, dest_dir: Path, root: str = "") -> None:
    """Descomprime `archive` (.zip, .tar.gz o .7z) en `dest_dir`. En un
    .zip, `root` es una carpeta raiz que se quita de las rutas (ver
    `archive_root`)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    shown = dest_dir.relative_to(ROOT) if dest_dir.is_relative_to(ROOT) else dest_dir
    print(f"  descomprimiendo {archive.name} en {shown}")
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            # Se validan todas las rutas antes de escribir nada.
            targets = []
            for info in zf.infolist():
                name = strip_archive_root(info.filename, root)
                if name is None or info.is_dir():
                    continue
                targets.append((info, safe_destination(dest_dir, name)))
            for info, dest in targets:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, dest.open("wb") as out:
                    shutil.copyfileobj(src, out)
        return
    if root:
        raise ValueError(f"archive_root solo se admite en .zip: {archive.name}")
    if py7zr.is_7zfile(archive):
        with py7zr.SevenZipFile(archive) as sz:
            # Igual que en el .zip: se validan todas las rutas antes de
            # escribir nada, y no se aceptan enlaces.
            for entry in sz.list():
                safe_destination(dest_dir, entry.filename)
                if entry.is_symlink:
                    raise ValueError(f"enlace no permitido en {archive.name}: {entry.filename}")
            sz.extractall(dest_dir)
        return
    with tarfile.open(archive) as tf:
        if hasattr(tarfile, "data_filter"):
            tf.extractall(dest_dir, filter="data")
        else:  # Python sin el filtro de seguridad de tarfile
            for member in tf.getmembers():
                safe_destination(dest_dir, member.name)
                if member.issym() or member.islnk():
                    raise ValueError(f"enlace no permitido en {archive.name}: {member.name}")
            tf.extractall(dest_dir)


def download_archive(source: DatasetSource, dataset_dir: Path, keep_archive: bool) -> None:
    archive = download_file(source.url, DOWNLOADS / source.archive_name, source.archive_size)
    extract_archive(archive, dataset_dir, source.archive_root)
    if not keep_archive:
        archive.unlink()
    for extra in source.extra_files:
        download_file(extra.url, safe_destination(dataset_dir, extra.name), extra.size)


def download_huggingface(source: DatasetSource, dataset_dir: Path) -> None:
    info = fetch_json(huggingface_revision_url(source.repo_id, source.revision))
    files = [s["rfilename"] for s in info.get("siblings", [])]
    for name in files:
        if name in HUGGINGFACE_SKIP:
            continue
        dest = safe_destination(dataset_dir, name)
        download_file(huggingface_file_url(source.repo_id, source.revision, name), dest)


def download_roboflow(
    source: DatasetSource, dataset_dir: Path, api_key: str, keep_archive: bool
) -> None:
    url = roboflow_export_url(source.workspace, source.project, source.version, api_key)
    export = fetch_json(url).get("export", {})
    link = export.get("link")
    if not link:
        raise RuntimeError(
            f"Roboflow no devolvio el link del export de {source.project} "
            f"v{source.version} (respuesta sin export.link)"
        )
    archive = download_file(link, DOWNLOADS / f"{source.folder}.zip")
    extract_archive(archive, dataset_dir)
    if not keep_archive:
        archive.unlink()


def load_roboflow_key() -> str | None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        pass
    else:
        load_dotenv(ROOT / ".env")
    return os.environ.get("ROBOFLOW_API_KEY") or None


def print_catalog() -> None:
    for source in DATASETS.values():
        share = "si" if source.shareable else "NO (cada uno lo descarga)"
        print(f"{source.key}\n  {source.title}\n  data/raw/{source.folder}/")
        print(f"  licencia: {source.license} | compartible entre integrantes: {share}")


def check_dataset(source: DatasetSource) -> list[str]:
    problems = check_layout(DATA_RAW / source.folder, source)
    status = "OK" if not problems else "INCOMPLETO"
    print(f"[{source.key}] {status}")
    for problem in problems:
        print(f"  - {problem}")
    return problems


def download_dataset(
    source: DatasetSource, force: bool, keep_archive: bool, roboflow_key: str | None
) -> bool:
    """Descarga un dataset si falta (o si `force`). Devuelve True si al
    terminar queda completo."""
    dataset_dir = DATA_RAW / source.folder
    if not force and not check_layout(dataset_dir, source):
        print(f"[{source.key}] ya esta completo en data/raw/{source.folder}/ - se omite")
        return True

    print(f"[{source.key}] descargando {source.title} ({source.license})")
    if source.method == "archive":
        download_archive(source, dataset_dir, keep_archive)
    elif source.method == "huggingface":
        download_huggingface(source, dataset_dir)
    elif source.method == "roboflow":
        if not roboflow_key:
            print(
                f"[{source.key}] se omite: falta ROBOFLOW_API_KEY (en el entorno o en .env). "
                "Alternativa: copiar el dataset desde otro integrante (licencia "
                f"{source.license}) a data/raw/{source.folder}/ y correr --check."
            )
            return False
        download_roboflow(source, dataset_dir, roboflow_key, keep_archive)
    else:
        raise ValueError(f"metodo de descarga desconocido: {source.method}")

    return not check_dataset(source)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dataset",
        choices=["all", *DATASETS.keys()],
        default="all",
        help="Dataset a descargar o verificar (default: all)",
    )
    parser.add_argument("--list", action="store_true", help="Muestra el catalogo y sale")
    parser.add_argument(
        "--check", action="store_true", help="Solo verifica data/raw/, sin descargar"
    )
    parser.add_argument(
        "--force", action="store_true", help="Descarga aunque el dataset ya este completo"
    )
    parser.add_argument(
        "--keep-archives",
        action="store_true",
        help="No borra los .zip/.tar.gz/.7z de data/raw/.downloads/ despues de descomprimir",
    )
    args = parser.parse_args()

    if args.list:
        print_catalog()
        return

    sources = (
        list(DATASETS.values()) if args.dataset == "all" else [DATASETS[args.dataset]]
    )
    if args.check:
        failed = [s.key for s in sources if check_dataset(s)]
    else:
        roboflow_key = load_roboflow_key()
        failed = [
            s.key
            for s in sources
            if not download_dataset(s, args.force, args.keep_archives, roboflow_key)
        ]

    if failed:
        print(f"\nIncompletos: {', '.join(failed)}")
        sys.exit(1)
    print("\nTodos los datasets pedidos estan completos.")


if __name__ == "__main__":
    main()
