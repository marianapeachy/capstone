# Graph Report - capstone  (2026-09-27)

## Corpus Check
- 51 files · ~119,133 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 7)

## Summary
- 575 nodes · 891 edges · 45 communities (32 shown, 13 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `939cd852`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- search_skills.py
- prepare_datasets.py
- skill-index.schema.json
- What You Must Do When Invoked
- Skill Finder VS Code Extension - Design Spec
- segment_gondola
- update_scientific_descriptions.py
- test_image_correction.py
- Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile)
- Search-Skills.ps1
- Agent Instructions
- graphify reference: extra exports and benchmark
- properties
- source
- properties
- ShelfVision AI - Walmart Chile
- skill-index.json
- visualize_segmentation.py
- graphify reference: query, path, explain
- category
- url
- skill
- id
- name
- Datasets - ShelfVision AI
- test_preprocessing.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- run_pipeline.py
- .claude/CLAUDE.md
- extraction-spec.md
- owner
- Bitácora de Sprint 1 - ShelfVision AI
- Setup Guide

## God Nodes (most connected - your core abstractions)
1. `segment_gondola()` - 23 edges
2. `main()` - 21 edges
3. `crop_roi()` - 18 edges
4. `LensCalibration` - 16 edges
5. `correct_image()` - 15 edges
6. `ShelfLine` - 14 edges
7. `dewarp()` - 14 edges
8. `Skill Finder VS Code Extension - Design Spec` - 14 edges
9. `apply_clahe()` - 13 edges
10. `Pendientes (priorizados)` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Pendientes (priorizados)` --references--> `ShelfLine`  [INFERRED]
  PROGRESS.md → src/preprocessing/gondola_segmentation.py
- `Pendientes (priorizados)` --references--> `GondolaSegmentation`  [INFERRED]
  PROGRESS.md → src/preprocessing/gondola_segmentation.py
- `Reglas de código` --references--> `segment_gondola()`  [INFERRED]
  CLAUDE.md → src/preprocessing/gondola_segmentation.py
- `Pendientes (priorizados)` --references--> `segment_gondola()`  [INFERRED]
  PROGRESS.md → src/preprocessing/gondola_segmentation.py
- `Pendientes (priorizados)` --references--> `RoiCrop`  [INFERRED]
  PROGRESS.md → src/preprocessing/roi_filter.py

## Import Cycles
- None detected.

## Communities (45 total, 13 thin omitted)

### Community 0 - "search_skills.py"
Cohesion: 0.06
Nodes (57): Any, add_source(), check_and_auto_update(), check_dependencies(), discover_new_repos(), find_similar_skills(), install_skill(), is_index_outdated() (+49 more)

### Community 1 - "prepare_datasets.py"
Cohesion: 0.12
Nodes (33): argparse, csv, Path, convert_kaggle_supermarket(), convert_roboflow_coco(), convert_sku110k(), convert_unidatapro(), main() (+25 more)

### Community 2 - "skill-index.schema.json"
Cohesion: 0.05
Nodes (38): additionalProperties, description, examples, items, minItems, type, description, pattern (+30 more)

### Community 3 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 4 - "Skill Finder VS Code Extension - Design Spec"
Cohesion: 0.08
Nodes (24): 2-Layer Structure, Agent Compatibility Matrix, Author, Commands, Core Concept, Dependencies, Development Notes, Enable/Disable by Comment (+16 more)

### Community 5 - "segment_gondola"
Cohesion: 0.10
Nodes (38): _band_texture(), _detect_shelf_lines(), _fit_line(), GondolaSegmentation, _profile_peaks(), ndarray, PixelBBox, Segmentacion automatica de la gondola y sus repisas (vision clasica). Corre… (+30 more)

### Community 6 - "update_scientific_descriptions.py"
Cohesion: 0.17
Nodes (15): get_skill_description(), main(), Fetch descriptions from various GitHub repositories and update skill-index.json, Fetch description from SKILL.md frontmatter, get_skill_description(), infer_categories(), main(), Infer categories from skill name and description (+7 more)

### Community 7 - "test_image_correction.py"
Cohesion: 0.09
Nodes (46): Reglas de código, cv2, Pendientes (priorizados), apply_clahe(), correct_image(), CorrectedImage, dewarp(), LensCalibration (+38 more)

### Community 8 - "Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile)"
Cohesion: 0.12
Nodes (15): 1. Dominio de Aplicación, 2. Supuestos del Dominio, Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile), 🎯 Definición del Alcance, 📌 Descripción General del Proyecto, Ejecución con Docker, Ejecución local, 👨‍💻 Equipo de Desarrollo (+7 more)

### Community 9 - "Search-Skills.ps1"
Cohesion: 0.23
Nodes (8): Find-NewRepos(), Get-SkillIndex(), Get-StarredSkills(), Invoke-AutoUpdateCheck(), Invoke-DiscoverNewRepos(), Search-LocalIndex(), Show-PostSearchSuggestions(), Test-IndexOutdated()

### Community 10 - "Agent Instructions"
Cohesion: 0.06
Nodes (32): Agent Behavior Rules, Agent Instructions, Checklist Before Responding, Collection Stewardship, Core Principle, 🚨 Mandatory Proposal Block, Output Format, Recommendation Workflow (+24 more)

### Community 11 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 12 - "properties"
Cohesion: 0.25
Nodes (8): description, type, description, type, properties, description, enum, type

### Community 13 - "source"
Cohesion: 0.29
Nodes (8): definitions, source, source, additionalProperties, description, examples, required, type

### Community 14 - "properties"
Cohesion: 0.40
Nodes (5): description, examples, type, path, properties

### Community 15 - "ShelfVision AI - Walmart Chile"
Cohesion: 0.29
Nodes (6): Comandos frecuentes, Continuidad entre sesiones / chats, Estructura relevante, graphify, Notas, ShelfVision AI - Walmart Chile

### Community 16 - "skill-index.json"
Cohesion: 0.29
Nodes (6): categories, $schema, lastUpdated, skills, sources, version

### Community 17 - "visualize_segmentation.py"
Cohesion: 0.09
Nodes (35): DataFrame, fixture, math, numpy, pandas, Protocol, pytest, contact_sheet() (+27 more)

### Community 18 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 19 - "category"
Cohesion: 0.33
Nodes (6): additionalProperties, description, properties, required, type, category

### Community 20 - "url"
Cohesion: 0.33
Nodes (6): url, description, examples, format, pattern, type

### Community 21 - "skill"
Cohesion: 0.40
Nodes (5): skill, additionalProperties, description, required, type

### Community 22 - "id"
Cohesion: 0.40
Nodes (5): description, examples, pattern, type, id

### Community 23 - "name"
Cohesion: 0.40
Nodes (5): description, examples, pattern, type, name

### Community 24 - "Datasets - ShelfVision AI"
Cohesion: 0.40
Nodes (4): Adicionales recomendados, Datasets - ShelfVision AI, Qué hacer con estos datasets (proceso), Ya identificados por el equipo

### Community 25 - "test_preprocessing.py"
Cohesion: 0.11
Nodes (29): dataclasses, crop_roi(), normalize_roi(), BBox, ndarray, PixelBBox, Recorte de la region de interes (ROI) sobre la gondola detectada. Parte del…, Imagen recortada junto con la ROI (en coordenadas de la imagen original) de la… (+21 more)

### Community 26 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 27 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 28 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 41 - "owner"
Cohesion: 0.50
Nodes (4): description, examples, type, owner

### Community 42 - "Bitácora de Sprint 1 - ShelfVision AI"
Cohesion: 0.50
Nodes (3): Bitácora de Sprint 1 - ShelfVision AI, Estado, Notas

### Community 43 - "Setup Guide"
Cohesion: 0.12
Nodes (15): 1. Install GitHub CLI, 2. Authenticate, 3. Verify, Categories, Community (type: `community`), Curated Lists (type: `awesome-list`), Installation, Official (type: `official`) (+7 more)

## Knowledge Gaps
- **190 isolated node(s):** `$schema`, `version`, `lastUpdated`, `sources`, `skills` (+185 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 314 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `segment_gondola()` connect `segment_gondola` to `visualize_segmentation.py`, `test_image_correction.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `correct_image()` connect `test_image_correction.py` to `visualize_segmentation.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `Pendientes (priorizados)` connect `test_image_correction.py` to `test_preprocessing.py`, `Bitácora de Sprint 1 - ShelfVision AI`, `segment_gondola`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `segment_gondola()` (e.g. with `Reglas de código` and `Pendientes (priorizados)`) actually correct?**
  _`segment_gondola()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `LensCalibration` (e.g. with `_distort()` and `test_correct_image_dewarps_before_clahe()`) actually correct?**
  _`LensCalibration` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `correct_image()` (e.g. with `Reglas de código` and `Pendientes (priorizados)`) actually correct?**
  _`correct_image()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `version`, `lastUpdated` to the rest of the system?**
  _190 weakly-connected nodes found - possible documentation gaps or missing edges._