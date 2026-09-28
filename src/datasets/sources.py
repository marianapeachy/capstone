"""Catalogo de los datasets publicos del proyecto: de donde se descargan,
bajo que licencia y que archivos deben quedar en data/raw/ (ver
docs/datasets.md).

Este modulo no usa la red: la descarga y la descompresion viven en
scripts/download_datasets.py. Aqui estan los datos del catalogo y las
funciones que se pueden probar sin conexion (URLs, rutas seguras y
verificacion de la estructura descargada).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlencode


@dataclass(frozen=True)
class ExpectedFiles:
    """Cantidad exacta de archivos que debe calzar con `pattern` (glob
    relativo a la carpeta del dataset) despues de descargarlo."""

    pattern: str
    count: int


@dataclass(frozen=True)
class RemoteFile:
    """Archivo suelto que se descarga tal cual (sin descomprimir) a
    `name`, relativo a la carpeta del dataset."""

    url: str
    name: str
    size: int | None = None  # bytes; detecta descargas truncadas


@dataclass(frozen=True)
class DatasetSource:
    """Un dataset del catalogo.

    `method` define como se descarga:
    - "archive": un .zip, .tar.gz o .7z desde `url`, que se descomprime en
      la carpeta del dataset, mas los `extra_files` que vienen aparte.
    - "huggingface": los archivos del repo `repo_id` en `revision`.
    - "roboflow": el export COCO de `workspace/project/version`; requiere
      API key de Roboflow.
    """

    key: str  # misma clave que usa scripts/prepare_datasets.py
    folder: str  # carpeta dentro de data/raw/
    title: str
    license: str
    shareable: bool  # si la licencia permite pasarse los archivos entre integrantes
    method: str
    expected: tuple[ExpectedFiles, ...]
    url: str = ""
    archive_name: str = ""
    archive_size: int | None = None  # bytes; detecta descargas truncadas
    archive_root: str = ""  # carpeta raiz del .zip que se quita al descomprimir
    extra_files: tuple[RemoteFile, ...] = ()
    repo_id: str = ""
    revision: str = ""
    workspace: str = ""
    project: str = ""
    version: int = 0


DATASETS: dict[str, DatasetSource] = {
    source.key: source
    for source in (
        DatasetSource(
            key="sku110k",
            folder="sku-110k",
            title="SKU-110K (Trax Retail, CVPR'19)",
            license="Academico y no comercial, sin redistribucion",
            shareable=False,
            method="archive",
            url="http://trax-geometry.s3.amazonaws.com/cvpr_challenge/SKU110K_fixed.tar.gz",
            archive_name="SKU110K_fixed.tar.gz",
            archive_size=12_196_152_718,
            expected=(
                ExpectedFiles("SKU110K_fixed/images/*.jpg", 11_743),
                ExpectedFiles("SKU110K_fixed/annotations/annotations_*.csv", 3),
            ),
        ),
        DatasetSource(
            key="kaggle_supermarket",
            folder="supermarket-shelves",
            title="Supermarket Shelves (Humans in the Loop, Kaggle)",
            license="CC0 1.0",
            shareable=True,
            method="archive",
            url=(
                "https://www.kaggle.com/api/v1/datasets/download/"
                "humansintheloop/supermarket-shelves-dataset?datasetVersionNumber=2"
            ),
            archive_name="supermarket-shelves-dataset.zip",
            # El zip trae todo dentro de "Supermarket shelves/" (y dentro otra
            # "Supermarket shelves/" con images/ y annotations/).
            archive_root="Supermarket shelves",
            expected=(
                ExpectedFiles("Supermarket shelves/images/*.jpg", 45),
                ExpectedFiles("Supermarket shelves/annotations/*.json", 45),
            ),
        ),
        DatasetSource(
            key="unidatapro",
            folder="grocery-shelves-unidatapro",
            title="Grocery Shelves sample (UniDataPro, Hugging Face)",
            license="CC BY-NC-ND 4.0",
            shareable=True,
            method="huggingface",
            repo_id="UniDataPro/grocery-shelves",
            revision="cfbf1e29eada9ebfd5740bfd1f6f8160ad0a631e",
            expected=(
                ExpectedFiles("annotations.xml", 1),
                ExpectedFiles("img/*", 15),
                ExpectedFiles("labels/*", 15),
            ),
        ),
        DatasetSource(
            key="roboflow_out_of_stock",
            folder="out-of-stock-detection-roboflow",
            title="Out Of Stock detection (Roboflow Universe)",
            license="CC BY 4.0",
            shareable=True,
            method="roboflow",
            workspace="empty-space-detection-capstone",
            project="out-of-stock-detection",
            version=1,
            expected=(
                ExpectedFiles("train/*.jpg", 3024),
                ExpectedFiles("train/_annotations.coco.json", 1),
            ),
        ),
        DatasetSource(
            key="roboflow_empty_shelf",
            folder="empty-shelf-detector-roboflow",
            title="Empty Shelf Detector (Roboflow Universe)",
            license="CC BY 4.0",
            shareable=True,
            method="roboflow",
            workspace="fyp-ormnr",
            project="empty-shelf-detector",
            version=1,
            expected=(
                ExpectedFiles("train/*.jpg", 291),
                ExpectedFiles("valid/*.jpg", 24),
                ExpectedFiles("test/*.jpg", 18),
                ExpectedFiles("*/_annotations.coco.json", 3),
            ),
        ),
        DatasetSource(
            key="shard",
            folder="shard",
            title="SHARD - SHelf mAnagement Row Dataset (figshare)",
            license="CC BY 4.0",
            shareable=True,
            method="archive",
            # IDs de archivo de la version 1 del articulo 24100695 de figshare.
            url="https://ndownloader.figshare.com/files/42285738",
            archive_name="shelf_detection.7z",
            archive_size=3_606_197_014,
            extra_files=(
                RemoteFile(
                    "https://ndownloader.figshare.com/files/42285732",
                    "annotation.csv",
                    1_631_733,
                ),
            ),
            # El .7z trae ademas una copia truncada de annotation.csv
            # (10,663 filas) y un tmp.png: la anotacion valida es la de
            # extra_files (22,745 filas, 22,743 imagenes; 2 repetidas).
            expected=(
                ExpectedFiles("shelf_detection/*.jpg", 22_743),
                ExpectedFiles("annotation.csv", 1),
            ),
        ),
    )
}

# Datasets que no anotan productos ni espacios vacios, asi que
# scripts/prepare_datasets.py no los convierte. SHARD anota la altura de
# cada repisa: se usa para evaluar la segmentacion (src/evaluation/).
ANNOTATION_ONLY = frozenset({"shard"})

# Archivos del repo de Hugging Face que no son parte del dataset.
HUGGINGFACE_SKIP = frozenset({".gitattributes"})


def check_layout(dataset_dir: Path, source: DatasetSource) -> list[str]:
    """Compara lo que hay en `dataset_dir` con lo esperado para `source`.

    Devuelve la lista de problemas encontrados; vacia si el dataset esta
    completo.
    """
    if not dataset_dir.is_dir():
        return [f"no existe la carpeta {dataset_dir}"]
    problems = []
    for item in source.expected:
        found = sum(1 for path in dataset_dir.glob(item.pattern) if path.is_file())
        if found != item.count:
            problems.append(f"{item.pattern}: {found} archivos, se esperaban {item.count}")
    return problems


def safe_destination(base_dir: Path, relative_name: str) -> Path:
    """Ruta dentro de `base_dir` para un archivo de un .zip o de un repo
    remoto. Rechaza rutas absolutas o con `..` que escaparian de la
    carpeta (path traversal) con `ValueError`."""
    posix = PurePosixPath(relative_name.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or ":" in relative_name:
        raise ValueError(f"ruta insegura en el archivo descargado: {relative_name!r}")
    return base_dir.joinpath(*posix.parts)


def strip_archive_root(name: str, root: str) -> str | None:
    """Quita la carpeta raiz `root` de una ruta dentro de un .zip.

    Devuelve None para lo que no queda dentro de `root` o es la carpeta
    misma (no se extrae). Con `root` vacio devuelve `name` sin cambios.
    """
    if not root:
        return name
    prefix = root.strip("/") + "/"
    normalized = name.replace("\\", "/")
    if not normalized.startswith(prefix):
        return None
    return normalized[len(prefix) :] or None


def huggingface_revision_url(repo_id: str, revision: str) -> str:
    """URL de la API que lista los archivos del dataset en esa revision."""
    return f"https://huggingface.co/api/datasets/{repo_id}/revision/{revision}"


def huggingface_file_url(repo_id: str, revision: str, filename: str) -> str:
    return f"https://huggingface.co/datasets/{repo_id}/resolve/{revision}/{quote(filename)}"


def roboflow_export_url(
    workspace: str, project: str, version: int, api_key: str, fmt: str = "coco"
) -> str:
    """URL de la API de Roboflow que responde con el link del ZIP del
    export (campo `export.link` del JSON)."""
    query = urlencode({"api_key": api_key})
    return f"https://api.roboflow.com/{workspace}/{project}/{version}/{fmt}?{query}"
