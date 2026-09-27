# Bitácora de Sprint 1 - ShelfVision AI

## Estado

Estructura inicial del repositorio creada (directorios `src/`, `tests/`,
`docs/`, `data/`, `scripts/`, más `.gitignore`, `requirements.txt`,
`Dockerfile`, `CLAUDE.md`).

## Pendientes (priorizados)

1. [ ] Implementar `src/preprocessing/roi_filter.py`: recortador de
       región de interés (ROI) sobre la góndola detectada, incluyendo
       normalización de coordenadas `[x_min, y_min, x_max, y_max]`.
2. [ ] Implementar pruebas unitarias en `tests/test_preprocessing.py`
       para `roi_filter.py` (casos: ROI dentro de límites, ROI fuera de
       límites, imagen vacía/None).
3. [ ] Implementar filtros CLAHE y dewarping en `src/preprocessing/`.
4. [ ] Integrar inferencia YOLOv8 en `src/models/`.
5. [ ] Implementar cálculo de disponibilidad y evaluación de umbral
       `<30%` en `src/postprocessing/`.
6. [ ] Implementar generación de reportes (Excel, CSV, PDF) en
       `src/reporting/`.
7. [ ] Implementar `scripts/run_pipeline.py` como CLI que orquesta el
       pipeline completo.
8. [ ] Documentar especificaciones técnicas y diagramas en `docs/`.
9. [x] Descargar datasets candidatos (ver `docs/datasets.md`):
       SKU-110K, grocery-shelves (UniDataPro), supermarket-shelves
       (Kaggle), Out Of Stock detection y Empty Shelf Detector
       (Roboflow) — los 5 ya están en `data/raw/`.
10. [x] Escribir conversores de anotaciones a nuestro estándar
       `[x_min, y_min, x_max, y_max]`: lógica pura en
       `src/datasets/converters.py` (probada en
       `tests/test_dataset_converters.py`, 8/8 tests OK) + CLI
       `scripts/prepare_datasets.py` que recorre `data/raw/` y escribe
       `data/processed/annotations/<dataset>.csv` +
       `all_annotations.csv` (1,760,633 anotaciones combinadas de los 5
       datasets). No versionado (`data/processed/*` en `.gitignore`).
11. [ ] Falta script de *descarga* reproducible (hoy la descarga se
       hizo manualmente); ver Notas.

## Notas

- La carpeta `Fase 1/` (entregables de la Fase 1 académica) no se toca.
- README.md se actualizará incrementalmente a medida que se implementen
  los módulos.
- Los 2 datasets de Roboflow se descargaron manualmente (export ZIP en
  formato COCO) porque la descarga programática requiere API key de
  Roboflow, que el equipo no tenía configurada. Pendiente decidir si se
  gestiona una API key para automatizar esto en `scripts/prepare_datasets.py`
  (hoy asume que los datos ya están en `data/raw/`).
