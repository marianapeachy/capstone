# ShelfVision AI - Walmart Chile

Sistema de auditoría automatizada de disponibilidad de stock en góndolas de
alimentos no perecibles, desarrollado para el Proyecto de Título (APT122 /
Capstone) de Duoc UC en colaboración con Walmart Chile.

## Reglas de código

- **Solo scripts `.py`**: no se usan notebooks (`.ipynb`) para el código
  core del pipeline. Notebooks solo se permiten como exploración puntual
  fuera de `src/`, nunca versionados.
- **Bounding boxes estandarizados**: toda coordenada de detección o
  anotación se representa como `[x_min, y_min, x_max, y_max]` en píxeles
  absolutos de la imagen original.
- **Enfoque híbrido obligatorio**: `src/preprocessing/` (OpenCV: CLAHE,
  dewarping, recorte de ROI) siempre precede a `src/models/` (YOLOv8).
  No se reemplaza el pre-procesamiento clásico por el modelo de inferencia.
- **Pipeline modular**: `preprocessing -> models -> postprocessing ->
  reporting`. Cada etapa vive en su propio paquete y no debe importar
  directamente detalles internos de otra etapa; se comunican mediante
  estructuras de datos simples (arrays, dicts, dataclasses).
- **Umbral de disponibilidad crítica**: `< 30%` de espacio disponible en
  la góndola dispara alerta (MVP Nivel 2, ver README).

## Estructura relevante

```
src/preprocessing/   # Filtros CLAHE, dewarping, recorte de ROI
src/models/           # Inferencia YOLOv8
src/postprocessing/    # Cálculo de disponibilidad y umbral <30%
src/reporting/         # Reportes en Excel, CSV y PDF
scripts/               # CLI de ejecución del pipeline
tests/                 # Pruebas unitarias con pytest
data/raw/              # Imágenes de entrada (no versionadas)
data/processed/        # Salidas intermedias/procesadas (no versionadas)
```

## Comandos frecuentes

```bash
pytest tests/
python scripts/run_pipeline.py
```

## Notas

- La carpeta `Fase 1/` contiene entregables académicos ya evaluados y no
  debe modificarse.
- Los pesos de modelos (`*.pt`, `*.onnx`) y las imágenes de datos no se
  versionan (ver `.gitignore`).

## Continuidad entre sesiones / chats

Este repositorio externaliza su estado a archivos, no a la memoria de una
conversación. Al empezar una sesión o chat nuevo (por compactación de
contexto o porque se abrió aparte), leer primero, en este orden:

1. `CLAUDE.md` (este archivo) - reglas de código y estructura.
2. `PROGRESS.md` - qué está hecho y qué es lo pendiente priorizado.
3. `docs/datasets.md` - estado y ubicación de los datasets descargados.

Con eso se recupera casi todo el contexto relevante sin necesitar el
historial de la conversación anterior.

Buen momento para compactar/cambiar de chat: justo después de cerrar un
hito (no a mitad de una tarea), especialmente antes de empezar un bloque
de trabajo grande y autocontenido (ej. implementar un módulo nuevo con
sus tests). Señal adicional: cuando las respuestas se sientan más lentas
o se repita contexto que ya debería estar resuelto.

Al terminar una tarea de esta bitácora, actualizar `PROGRESS.md` (marcar
lo hecho, agregar lo nuevo pendiente) antes de cerrar la sesión.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
