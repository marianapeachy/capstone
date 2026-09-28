from pathlib import Path

import importlib.util
import struct
import zlib

import py7zr
import pytest

from src.datasets.sources import (
    ANNOTATION_ONLY,
    DATASETS,
    DatasetSource,
    ExpectedFiles,
    check_layout,
    huggingface_file_url,
    roboflow_export_url,
    safe_destination,
    strip_archive_root,
)

TINY = DatasetSource(
    key="tiny",
    folder="tiny",
    title="Dataset de prueba",
    license="CC0",
    shareable=True,
    method="archive",
    expected=(ExpectedFiles("images/*.jpg", 2), ExpectedFiles("labels.json", 1)),
)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


ROOT = Path(__file__).resolve().parent.parent


def _load_download_script():
    spec = importlib.util.spec_from_file_location(
        "download_datasets", ROOT / "scripts" / "download_datasets.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_keys_match_prepare_datasets_converters():
    # scripts/prepare_datasets.py usa estas mismas claves en --dataset; los
    # de ANNOTATION_ONLY no tienen conversor de bboxes (anotan otra cosa).
    assert set(DATASETS) - ANNOTATION_ONLY == {
        "unidatapro",
        "kaggle_supermarket",
        "sku110k",
        "roboflow_out_of_stock",
        "roboflow_empty_shelf",
    }
    assert ANNOTATION_ONLY <= set(DATASETS)
    for key, source in DATASETS.items():
        assert source.key == key
        assert source.expected, f"{key} sin archivos esperados"


def test_sku110k_is_not_shareable():
    # Su licencia prohibe redistribuirlo: cada integrante lo descarga.
    assert DATASETS["sku110k"].shareable is False


def test_shard_downloads_7z_and_annotation_csv_from_pinned_figshare_files():
    shard = DATASETS["shard"]
    assert shard.license == "CC BY 4.0" and shard.shareable
    assert shard.method == "archive"
    # IDs de archivo de figshare (version 1 del articulo 24100695): fijos.
    assert shard.url == "https://ndownloader.figshare.com/files/42285738"
    assert shard.archive_name == "shelf_detection.7z"
    assert shard.archive_size == 3_606_197_014
    assert [(f.url, f.name, f.size) for f in shard.extra_files] == [
        ("https://ndownloader.figshare.com/files/42285732", "annotation.csv", 1_631_733)
    ]
    assert "shard" in ANNOTATION_ONLY


def test_extract_archive_supports_7z(tmp_path):
    archive = tmp_path / "data.7z"
    with py7zr.SevenZipFile(archive, "w") as sz:
        sz.writestr(b"a", "images/1.jpg")
        sz.writestr(b"bb", "images/sub/2.jpg")
    dest = tmp_path / "out"
    _load_download_script().extract_archive(archive, dest)
    assert (dest / "images" / "1.jpg").read_bytes() == b"a"
    assert (dest / "images" / "sub" / "2.jpg").read_bytes() == b"bb"


def _write_7z_with_raw_name(archive: Path, safe_name: str, raw_name: str) -> None:
    """.7z con un archivo llamado `raw_name` (ej. con `..`), que py7zr no
    deja escribir: se escribe como `safe_name` (mismo largo) con el
    encabezado sin comprimir, se reemplaza el nombre y se recalculan los
    CRC del encabezado."""
    assert len(safe_name) == len(raw_name)
    sz = py7zr.SevenZipFile(archive, "w")
    sz.encoded_header_mode = False
    sz.writestr(b"ok", "images/ok.jpg")
    sz.writestr(b"x", safe_name)
    sz.close()
    data = bytearray(
        archive.read_bytes().replace(safe_name.encode("utf-16-le"), raw_name.encode("utf-16-le"))
    )
    offset, size = struct.unpack_from("<QQ", data, 12)
    struct.pack_into("<I", data, 28, zlib.crc32(data[32 + offset : 32 + offset + size]))
    struct.pack_into("<I", data, 8, zlib.crc32(data[12:32]))
    archive.write_bytes(data)


def test_extract_archive_rejects_7z_path_traversal_before_writing(tmp_path):
    archive = tmp_path / "evil.7z"
    _write_7z_with_raw_name(archive, "XX/evil.txt", "../evil.txt")
    dest = tmp_path / "out"
    with pytest.raises(ValueError):
        _load_download_script().extract_archive(archive, dest)
    assert not (tmp_path / "evil.txt").exists()
    assert not (dest / "images" / "ok.jpg").exists()


def test_check_layout_ok_when_counts_match(tmp_path):
    _touch(tmp_path / "images" / "a.jpg")
    _touch(tmp_path / "images" / "b.jpg")
    _touch(tmp_path / "labels.json")
    assert check_layout(tmp_path, TINY) == []


def test_check_layout_reports_missing_and_extra_files(tmp_path):
    _touch(tmp_path / "images" / "a.jpg")
    problems = check_layout(tmp_path, TINY)
    assert problems == [
        "images/*.jpg: 1 archivos, se esperaban 2",
        "labels.json: 0 archivos, se esperaban 1",
    ]


def test_check_layout_ignores_directories_matching_pattern(tmp_path):
    (tmp_path / "images" / "fake.jpg").mkdir(parents=True)
    _touch(tmp_path / "labels.json")
    assert check_layout(tmp_path, TINY) == ["images/*.jpg: 0 archivos, se esperaban 2"]


def test_check_layout_missing_folder(tmp_path):
    problems = check_layout(tmp_path / "no-existe", TINY)
    assert len(problems) == 1
    assert "no existe la carpeta" in problems[0]


def test_safe_destination_keeps_nested_paths_inside_base(tmp_path):
    dest = safe_destination(tmp_path, "Supermarket shelves/images/001.jpg")
    assert dest == tmp_path / "Supermarket shelves" / "images" / "001.jpg"


@pytest.mark.parametrize(
    "name",
    ["../evil.txt", "img/../../evil.txt", "/etc/passwd", "..\\evil.txt", "C:/evil.txt"],
)
def test_safe_destination_rejects_path_traversal(tmp_path, name):
    with pytest.raises(ValueError):
        safe_destination(tmp_path, name)


def test_strip_archive_root_removes_top_folder():
    root = "Supermarket shelves"
    assert (
        strip_archive_root("Supermarket shelves/Supermarket shelves/images/1.jpg", root)
        == "Supermarket shelves/images/1.jpg"
    )
    assert strip_archive_root("Supermarket shelves/meta.json", root) == "meta.json"


def test_strip_archive_root_skips_outside_entries_and_root_itself():
    assert strip_archive_root("otra/cosa.txt", "Supermarket shelves") is None
    assert strip_archive_root("Supermarket shelves/", "Supermarket shelves") is None


def test_strip_archive_root_without_root_keeps_name():
    assert strip_archive_root("train/a.jpg", "") == "train/a.jpg"


def test_huggingface_file_url_pins_revision_and_quotes_path():
    url = huggingface_file_url("UniDataPro/grocery-shelves", "abc123", "img/11 b.jpeg")
    assert url == (
        "https://huggingface.co/datasets/UniDataPro/grocery-shelves/resolve/abc123/img/11%20b.jpeg"
    )


def test_roboflow_export_url_encodes_api_key():
    url = roboflow_export_url("ws", "proj", 1, "k&y")
    assert url == "https://api.roboflow.com/ws/proj/1/coco?api_key=k%26y"
