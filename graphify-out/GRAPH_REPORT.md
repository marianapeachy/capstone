# Graph Report - capstone  (2026-09-27)

## Corpus Check
- 42 files · ~113,429 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 7)

## Summary
- 449 nodes · 569 edges · 41 communities (29 shown, 12 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `993eae11`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- search_skills.py
- prepare_datasets.py
- properties
- What You Must Do When Invoked
- Skill Finder VS Code Extension - Design Spec
- Agent Instructions
- update_scientific_descriptions.py
- Setup Guide
- Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile)
- Search-Skills.ps1
- Skill Finder
- graphify reference: extra exports and benchmark
- properties
- source
- properties
- ShelfVision AI - Walmart Chile
- skill-index.json
- skill-index.schema.json
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

## God Nodes (most connected - your core abstractions)
1. `main()` - 21 edges
2. `crop_roi()` - 18 edges
3. `Skill Finder VS Code Extension - Design Spec` - 14 edges
4. `load_index()` - 12 edges
5. `What You Must Do When Invoked` - 12 edges
6. `clip_bbox()` - 11 edges
7. `/graphify` - 11 edges
8. `Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile)` - 11 edges
9. `normalize_roi()` - 10 edges
10. `Skill Finder` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Reglas de código` --references--> `crop_roi()`  [INFERRED]
  CLAUDE.md → src/preprocessing/roi_filter.py
- `Pendientes (priorizados)` --references--> `RoiCrop`  [INFERRED]
  PROGRESS.md → src/preprocessing/roi_filter.py
- `Pendientes (priorizados)` --references--> `normalize_roi()`  [INFERRED]
  PROGRESS.md → src/preprocessing/roi_filter.py
- `Pendientes (priorizados)` --references--> `crop_roi()`  [INFERRED]
  PROGRESS.md → src/preprocessing/roi_filter.py
- `test_class_group_defaults_to_other_for_unknown_class()` --calls--> `class_group()`  [EXTRACTED]
  tests/test_dataset_converters.py → src/datasets/converters.py

## Import Cycles
- None detected.

## Communities (41 total, 12 thin omitted)

### Community 0 - "search_skills.py"
Cohesion: 0.06
Nodes (58): Any, add_source(), check_and_auto_update(), check_dependencies(), discover_new_repos(), find_similar_skills(), install_skill(), is_index_outdated() (+50 more)

### Community 1 - "prepare_datasets.py"
Cohesion: 0.12
Nodes (33): argparse, csv, Path, convert_kaggle_supermarket(), convert_roboflow_coco(), convert_sku110k(), convert_unidatapro(), main() (+25 more)

### Community 2 - "properties"
Cohesion: 0.07
Nodes (32): description, examples, items, minItems, type, pattern, $ref, type (+24 more)

### Community 3 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 4 - "Skill Finder VS Code Extension - Design Spec"
Cohesion: 0.08
Nodes (24): 2-Layer Structure, Agent Compatibility Matrix, Author, Commands, Core Concept, Dependencies, Development Notes, Enable/Disable by Comment (+16 more)

### Community 5 - "Agent Instructions"
Cohesion: 0.15
Nodes (13): Agent Behavior Rules, Agent Instructions, Checklist Before Responding, Collection Stewardship, Core Principle, 🚨 Mandatory Proposal Block, Output Format, Recommendation Workflow (+5 more)

### Community 6 - "update_scientific_descriptions.py"
Cohesion: 0.17
Nodes (15): get_skill_description(), main(), Fetch descriptions from various GitHub repositories and update skill-index.json, Fetch description from SKILL.md frontmatter, get_skill_description(), infer_categories(), main(), Infer categories from skill name and description (+7 more)

### Community 7 - "Setup Guide"
Cohesion: 0.12
Nodes (15): 1. Install GitHub CLI, 2. Authenticate, 3. Verify, Categories, Community (type: `community`), Curated Lists (type: `awesome-list`), Installation, Official (type: `official`) (+7 more)

### Community 8 - "Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile)"
Cohesion: 0.12
Nodes (15): 1. Dominio de Aplicación, 2. Supuestos del Dominio, Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile), 🎯 Definición del Alcance, 📌 Descripción General del Proyecto, Ejecución con Docker, Ejecución local, 👨‍💻 Equipo de Desarrollo (+7 more)

### Community 9 - "Search-Skills.ps1"
Cohesion: 0.23
Nodes (8): Find-NewRepos(), Get-SkillIndex(), Get-StarredSkills(), Invoke-AutoUpdateCheck(), Invoke-DiscoverNewRepos(), Search-LocalIndex(), Show-PostSearchSuggestions(), Test-IndexOutdated()

### Community 10 - "Skill Finder"
Cohesion: 0.10
Nodes (19): Collection Management, Customization Routing, Decide Whether the User Needs a Skill, Fast Rules, Recommendation Heuristics, Response Pattern, Agent Instructions, Command Reference (+11 more)

### Community 11 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 12 - "properties"
Cohesion: 0.22
Nodes (9): description, examples, type, owner, type, properties, description, enum (+1 more)

### Community 13 - "source"
Cohesion: 0.29
Nodes (8): definitions, source, source, additionalProperties, description, examples, required, type

### Community 14 - "properties"
Cohesion: 0.25
Nodes (8): description, type, description, examples, type, description, path, properties

### Community 15 - "ShelfVision AI - Walmart Chile"
Cohesion: 0.25
Nodes (7): Comandos frecuentes, Continuidad entre sesiones / chats, Estructura relevante, graphify, Notas, Reglas de código, ShelfVision AI - Walmart Chile

### Community 16 - "skill-index.json"
Cohesion: 0.29
Nodes (6): categories, $schema, lastUpdated, skills, sources, version

### Community 17 - "skill-index.schema.json"
Cohesion: 0.29
Nodes (6): additionalProperties, description, required, $schema, title, type

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
Cohesion: 0.07
Nodes (39): dataclasses, fixture, math, numpy, parametrize, PixelBBox, Bitácora de Sprint 1 - ShelfVision AI, Estado (+31 more)

### Community 26 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 27 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 28 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **190 isolated node(s):** `$schema`, `version`, `lastUpdated`, `sources`, `skills` (+185 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 278 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `properties` connect `properties` to `skill-index.schema.json`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `properties` connect `properties` to `properties`, `source`, `skill`, `name`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `categories` connect `properties` to `properties`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `crop_roi()` (e.g. with `Reglas de código` and `Pendientes (priorizados)`) actually correct?**
  _`crop_roi()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `version`, `lastUpdated` to the rest of the system?**
  _190 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `search_skills.py` be split into smaller, more focused modules?**
  _Cohesion score 0.061952074810052604 - nodes in this community are weakly interconnected._
- **Should `prepare_datasets.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11587301587301588 - nodes in this community are weakly interconnected._