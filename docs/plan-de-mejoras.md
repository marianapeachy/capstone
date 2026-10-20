# Plan de mejoras de la Fase 1

Ítem #26 de `PROGRESS.md`. Elaborado el 2026-10-20 por Mariana Ramírez.
El plazo del curso era el 2026-10-09 (semana 8), así que se entrega con
atraso; la Carta Gantt de la Fase 2 lo registra así. Algunas mejoras se
implementaron antes de escribir este documento; la columna "Estado" lo
indica.

Los responsables y las fechas de las mejoras sin dueño en `PROGRESS.md`
son **propuestas**: el equipo las confirma en su próxima reunión.

## 1. Punto de partida

La Fase 1 se evaluó con nota 7,0. La `PLANILLA DE EVALUACIÓN FASE 1.xlsx`
marca "Completamente logrado" en todos los indicadores, grupales e
individuales, y no registra observaciones. La formativa 1.4 tampoco trae
sugerencias escritas. Por eso el plan no responde a observaciones del
docente, sino a tres fuentes:

1. **Lo comprometido en la Fase 1 contra lo que el proyecto es hoy.** Se
   revisaron la guía 1.5 (definición del proyecto) y los anexos de
   `Anexos/Diseño/` y `Anexos/Gestion/`.
2. **Lo que evalúa el avance de la Fase 2:**
   - la planilla de evaluación del avance;
   - las pautas 2.2 y 2.3;
   - la guía 2.4.

   El detalle está en "Requisitos vigentes" de `docs/curso.md`.
3. **Los cambios que pidieron el cliente y el docente:**
   - acuerdos con Walmart, en el README;
   - mensajes del profesor, en `docs/curso.md`;
   - el cambio de alcance del 2026-10-19 (#40).

## 2. Diagnóstico

| # | Aspecto | Fase 1 | Situación al 2026-10-20 | Criterio de la Fase 2 afectado |
| --- | --- | --- | --- | --- |
| M1 | Objetivos | Dos objetivos específicos en una sola línea, sin metas que se puedan medir | Hay métricas reales (F1 de repisas, mAP, IoU), pero ningún objetivo las fija como meta | Ajustes justificados (10) y metodología (10) |
| M2 | Metodología | Dice que se entrenaría un modelo que reconoce espacios vacíos, usando Google Colab | El pipeline es híbrido: OpenCV corrige la imagen y segmenta la góndola, y YOLO26 detecta productos; el vacío se deduce de lo que no está cubierto por productos. Se entrena en una GPU local y se trabaja con TDD, PR y CI. El ajuste está en el README, pero en ningún entregable del curso | Ajustes justificados (10) y metodología (10) |
| M3 | Factibilidad y riesgos | Dice que "no existen impedimentos" y que Walmart entregó las imágenes. La matriz de riesgo fija bbox `[x, y, ancho, alto]` y un límite de 2 GB de VRAM | Varios supuestos no se cumplieron: (a) Walmart no comparte fotogramas de sus cámaras ni el Dataset Oculto (#21); (b) la licencia de SKU-110K impide mostrar o modificar sus fotos; (c) el alcance cambió (#40); (d) el servidor del CITT está bloqueado (#39). Además, el estándar del proyecto es `[x_min, y_min, x_max, y_max]` y el detector se entrena en 8 GB | Ajustes justificados (10) |
| M4 | Evidencias | Una sola evidencia de avance ("Informe de Análisis y Preprocesamiento de Dataset") y el texto de instrucciones de la plantilla sin borrar | Hay muchas más evidencias, pero ninguna lista las conecta con los objetivos | Evidencias de documentación, programación y datos (25) y documentación en Git (20) |
| M5 | Plan de trabajo y Gantt | Las tablas 7 (plan de trabajo) y 8 (Gantt) de la guía quedaron vacías. La Gantt aparte tiene una actividad que termina antes de empezar | Ya existe `Anexos/Gestion/Carta Gantt Fase 2.xlsx`, con el estado de cada actividad. Falta la tabla de monitoreo de la guía 2.4 | Ajustes justificados (10) y gestión de proyectos (indicador de calidad) |
| M6 | Diseño contra lo construido | Los C.U, la arquitectura y la RACI hablan de API REST, JWT, React y YOLOv8. Los mockups traen un editor de ROI manual | La app es Django con sesiones (#28) y usa YOLO26. La ROI es automática y el umbral es "espacio libre ≥ 30%". Qué cambiar en cada documento: `docs/cambios-cu.md` | Documentación con estructura pedida (20). En las evidencias de avance se comparan diseño y sistema |
| M7 | Competencias | La guía nombra tres competencias del perfil de egreso | La pauta de avance revisa indicadores de calidad que la Fase 1 no relaciona: pruebas de validación, modelos de datos, integración e implantación | Indicadores de calidad del perfil de egreso (pautas 2.2 y 2.3) |
| M8 | Inglés | La guía 1.5 no tiene abstract ni conclusiones en inglés | Las pautas 2.2 y 2.3 piden abstract en español e inglés, conclusiones y reflexiones individuales en inglés, y nivel intermedio alto | Redacción (5) e inglés (pautas 2.2 y 2.3) |
| M9 | Aporte de cada integrante | No se definió cómo se vería en el repositorio | 36 de los 40 PR mergeados vienen de una sola cuenta (al 2026-10-20), y los commits aparecen con 6 identidades de autor para 3 integrantes | Aporte de cada integrante visible en el repositorio (15) y trabajo en equipo (10) |
| M10 | Validación en condiciones del cliente | Se suponía que se trabajaría con imágenes de Walmart | El detector solo está medido en el test de SKU-110K (#33). No hay fotos propias (#32) ni fotos de cámara de sala (#14) | Evidencias (25) y pruebas de validación (indicador de calidad) |

## 3. Plan de acción

Estados posibles: No iniciado, En curso, Completado, Ajustada.

| # | Mejora | Acciones | Responsable | Fecha | Evidencia de cumplimiento | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | Objetivos medibles | Usar los objetivos de la sección 4 en el informe intermedio y en la guía 2.4, cada uno con su meta y su resultado actual | Francisco (informe, #27); Mariana (guía 2.4, #37) | 2026-10-21 (informe); 2026-10-26 (guía) | Objetivos con meta en el informe y en la guía 2.4 | En curso (propuesta en este documento) |
| M2 | Metodología ajustada y justificada | Describir el pipeline híbrido y por qué reemplazó al plan de la Fase 1, en el README (#35) y en la sección "ajustes" de la guía 2.4 | Francisco (#35); Mariana (#37) | 2026-10-21; 2026-10-26 | README, sección "Estrategia Algorítmica y Arquitectura"; guía 2.4 | En curso |
| M3 | Riesgos reales | Actualizar `MATRIZ DE RIESGO.xlsx`. Agregar: falta de imágenes de Walmart, licencia de SKU-110K, cambios de alcance, servidor del CITT y aporte desigual en el repositorio, cada uno con su mitigación. Corregir el formato de bbox y el límite de VRAM | Mariana (propuesto) | 2026-10-24 | Matriz actualizada en `Anexos/Gestion/` | No iniciado |
| M4 | Evidencias conectadas a los objetivos | Usar la tabla de la sección 5 en la guía 2.4 y en el anexo de evidencias del informe. Cada evidencia debe ser un archivo o un enlace en Git | Mariana (#37) | 2026-10-26 | Tabla de evidencias en la guía 2.4 | En curso (tabla en este documento) |
| M5 | Monitoreo del plan | Armar la tabla de la guía 2.4 a partir de la Gantt de la Fase 2 (columnas: competencia, actividad, recursos, duración, responsable, observaciones, estado y ajustes). Actualizar la Gantt en cada PR que cierre un ítem | Mariana (#37); cada dueño de ítem | 2026-10-26; continuo | Guía 2.4 y Gantt de la Fase 2 al día | En curso (Gantt de la Fase 2 creada en el PR #34) |
| M6 | Diseño alineado con el sistema | Rehacer las plantillas de C.U, los diagramas de secuencia y el de arquitectura según `docs/cambios-cu.md` (#42). Reemplazar los mockups del editor de ROI por capturas de la app web. Actualizar la RACI | Por asignar (#42) | 2026-10-26 | Anexos de `Anexos/Diseño/` actualizados | En curso (lista de cambios en `docs/cambios-cu.md`) |
| M7 | Competencias con evidencia | Agregar a la guía 2.4 la tabla de la sección 6, que liga cada indicador de calidad con su evidencia | Mariana (#37) | 2026-10-26 | Tabla en la guía 2.4 | En curso (tabla en este documento) |
| M8 | Inglés | Escribir el abstract en español e inglés del informe intermedio. Cada integrante escribe en inglés sus conclusiones y su reflexión individual. Otro integrante las revisa antes de entregar | Francisco (abstract, #27); cada integrante (reflexión) | 2026-10-21; 2026-10-26 | Informe intermedio y evidencias de avance | No iniciado |
| M9 | Aporte visible y equitativo | (a) Cada integrante confirma sus correos de commit y se agrega un `.mailmap` que unifica las 6 identidades. (b) Cada integrante abre los PR de sus propios ítems: #7 Mariana, #29 y #38 Nicko. (c) Aunque `main` ya no exige aprobación, cada PR lo revisa otro integrante y deja su comentario | Equipo | 2026-10-24 (a); continuo (b, c) | `git shortlog -sne` con 3 autores; PR de los 3 integrantes con revisiones cruzadas | No iniciado |
| M10 | Validación fuera de SKU-110K | Medir el detector con Kaggle CC0, con vistas oblicuas y con los datasets de Roboflow (#33). Conseguir fotos propias en tienda con permiso (#32). Generar imágenes tipo cámara de sala (#14) | Francisco (#33); por asignar (#32, #14) | 2026-10-21 (#33); 2026-10-31 (#32) | Resultados en `docs/test-plan.md` | En curso |

## 4. Objetivos específicos propuestos

Reemplazan los de la guía 1.5. El objetivo general no cambia. Cada uno
tiene una meta que se puede medir y su resultado al 2026-10-20.

| Objetivo específico | Meta | Resultado actual | Fuente |
| --- | --- | --- | --- |
| OE1. Segmentar automáticamente la góndola y sus repisas con visión clásica (OpenCV), antes del detector | F1 de repisas ≥ 0,80 en SHARD (tolerancia del 3% del alto) | 0,823 en una muestra de 1000 fotos no usada para ajustar | #15, `scripts/evaluate_shard.py` |
| OE2. Detectar productos en góndolas densas con YOLO26 | mAP50 ≥ 0,70 fuera de SKU-110K (referencia de Walmart) | 0,950 en el test de SKU-110K; fuera de SKU-110K, por medir | #5, #33 |
| OE3. Calcular el % libre de la góndola completa y alertar el quiebre con espacio libre ≥ 30% | Diferencia con el % libre anotado, a fijar con los resultados de #34 | Funciona en el pipeline; falta medirlo contra fotos anotadas | #6, #40, #34 |
| OE4. Entregar el sistema en una app web con login por rol (CU00 a CU06) | 7 C.U implementados; 50% para la Evaluación 2 | Hechos: login, usuarios y roles, carga y análisis de fotos, alertas. Pendientes: dashboard (#43), reportes (#7), configuración (#44) | #28, `docs/cambios-cu.md` |
| OE5. Validar cada cambio con pruebas automatizadas y cada versión con evaluación por lotes | CI en verde en cada PR; IoU por lote (CU07) | CI con pytest y `docker build` en cada PR; modo por lotes en `scripts/run_pipeline.py` | #13, #8 |

## 5. Evidencias de avance

| Evidencia | Dónde está | Qué demuestra | Objetivo |
| --- | --- | --- | --- |
| Segmentación medida contra SHARD | `scripts/evaluate_shard.py`, #15 en `PROGRESS.md` | Repisas detectadas contra repisas anotadas: precisión, recall y F1 | OE1 |
| Entrenamiento y métricas del detector | `docs/training.md` (cómo se entrena) y #5 en `PROGRESS.md` (métricas) | Configuración y mAP de YOLO26 en el test de SKU-110K | OE2 |
| Plan de pruebas y resultados | `docs/test-plan.md` | Casos de prueba y resultados por módulo | OE2, OE3, OE5 |
| Pipeline completo y evaluación por lotes | `scripts/run_pipeline.py`, `src/pipeline.py` | Una foto se convierte en % libre, alerta e imagen anotada; un lote se evalúa con IoU | OE3, OE5 |
| App web y base de datos | `web/`, `docs/auditoria-app-web.md` | Login por rol, CRUD de usuarios, análisis y alertas guardados en SQLite | OE4 |
| Pruebas automatizadas y CI | `tests/`, `.github/workflows/ci.yml` | Cada PR corre pytest y construye la imagen Docker | OE5 |
| Gestión del proyecto | `PROGRESS.md`, `Anexos/Gestion/Carta Gantt Fase 2.xlsx`, historial de PR | Dueño y estado de cada ítem, y revisión de cada cambio | Todos |
| Datasets y licencias | `docs/datasets.md`, `scripts/download_datasets.py` | Origen, licencia y descarga reproducible de cada dataset | OE1, OE2 |
| Informe intermedio y video | Entrega del 2026-10-21 | Estado real, mejores y peores casos, demostración | Todos |

## 6. Competencias e indicadores de calidad

Indicadores de calidad de las pautas 2.2 y 2.3 (los mismos de la
formativa 1.4) y la evidencia que cubre cada uno.

| Indicador de calidad | Evidencia | Brecha |
| --- | --- | --- |
| Diseña y aplica pruebas de validación (1.1, 1.2) | `docs/test-plan.md`, `tests/`, CI, evaluación con SHARD | Falta validar con imágenes del cliente o propias (M10) |
| Desarrolla mejoras a partir de las pruebas (1.3) | #15 (segmentación de 0,758 a 0,823 de F1), #22 (repisas inclinadas) | Ninguna |
| Planifica y controla el proyecto (2.1, 2.2) | `PROGRESS.md`, Gantt de la Fase 2, este plan | Tabla de monitoreo de la guía 2.4 (M5) |
| Diseña e implementa modelos de datos (3.1, 3.2) | Modelos y migraciones de Django en `web/` | El diseño de la base no está documentado fuera del código; agregar un diagrama con #42 |
| Construye la solución (4.1) | `src/`, `web/` | Ninguna |
| Integra los componentes (4.2) | `src/pipeline.py` integra las 4 etapas; la app web llama al pipeline | Reportes (#7) y dashboard (#43) aún sin integrar |
| Implanta la solución (4.3) | Imagen Docker y CI | Instalación en el servidor del CITT bloqueada (#39) |

## 7. Seguimiento

- **Dónde:** el estado de M1 a M10 se actualiza en la columna "Estado"
  de la sección 3, por PR, junto con el ítem de `PROGRESS.md` que cierre
  cada mejora.
- **Cuándo:** en cada taller, el equipo revisa las mejoras que siguen
  "No iniciado" o "En curso" y reasigna las que estén atrasadas. Es la
  misma acción de mitigación que la matriz de riesgo de la Fase 1 define
  para "Retraso en la Agenda".
- **Cierre:** el plan queda cumplido cuando M1 a M10 están "Completado"
  o "Ajustada" con su justificación. Esto se registra en las evidencias
  de avance (2026-10-26) y en la entrega final de la Fase 2.
