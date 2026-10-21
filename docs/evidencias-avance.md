# Evidencias de avance de la Fase 2 (borrador)

Ítem #37 de `PROGRESS.md`. Plazo: 2026-10-26. Responsable: Mariana
Ramírez. Borrador del 2026-10-20.

Este documento junta el contenido de dos evidencias de avance, con la
estructura que describe "Requisitos vigentes" en `docs/curso.md`:

- **Guía 2.4** (`2.4_GuiaEstudiante_Fase 2_DesarrolloProyecto APT.docx`),
  en la parte A.
- **Diario de reflexión 2.1**
  (`Apellido_Nombre_2.1_APT122_DiarioReflexionFase2.docx`), en la parte B.

**Estado:**

- **Parte A:** ya está en la plantilla oficial, en
  `Fase 2/2.4_GuiaEstudiante_Fase 2_DesarrolloProyecto APT.docx`
  (2026-10-20).
- **Parte B:** espera la plantilla 2.1, que no venía en la carpeta
  subida al repositorio (PR #42).

Las partes marcadas **[A completar por el equipo]** son opiniones o
datos que el repositorio no registra.

Datos al corte del 2026-10-20. Fuentes: `PROGRESS.md`,
`Anexos/Gestion/Carta Gantt Fase 2.xlsx`, `docs/plan-de-mejoras.md`, el
historial de Pull Requests y el README.

---

## Parte A. Guía 2.4: desarrollo del proyecto

### A.1 Resumen del avance

**Actividades realizadas (2026-09-27 a 2026-10-20).** El pipeline de
visión artificial está completo y funcionando. Toma una foto de góndola y
entrega el % de espacio libre de la góndola completa, la alerta de quiebre
(espacio libre ≥ 30%) y la imagen anotada. Sus etapas son:

1. Corrección de imagen: dewarping y CLAHE (#3).
2. Segmentación automática de la góndola y sus repisas con OpenCV (#4,
   #15).
3. Detección de productos con YOLO26, entrenado sobre SKU-110K (#5).
4. Cálculo de disponibilidad (#6), con repisas inclinadas para cámaras en
   ángulo (#22).
5. Pipeline completo por foto y evaluación por lotes con IoU (#8).

Además, hay una aplicación web en Django (#28) con:

- login por perfil (CU00);
- gestión de usuarios y roles (CU06);
- carga y análisis de fotos (CU01);
- alertas con estado para el reponedor (CU02).

En gestión, se armó un flujo de trabajo con ramas, Pull Requests,
integración continua y una bitácora (`PROGRESS.md`), y se mantienen la
Carta Gantt de la Fase 2 y el plan de mejoras de la Fase 1.

**Objetivos específicos cumplidos y cómo.** Los dos objetivos
específicos de la Fase 1 se cumplen así:

| Objetivo de la Fase 1 | Cómo se cumple |
| --- | --- |
| Diseñar un algoritmo propio con tecnologías actuales para el análisis de imágenes | Pipeline híbrido propio: visión clásica (OpenCV) para corregir la imagen y encontrar la góndola y sus repisas, y YOLO26 (Ultralytics, versión de 2026) para detectar productos. El espacio libre se deduce de lo que no cubren los productos dentro de cada repisa |
| Procesar imágenes del entorno de operación para distinguir un espacio libre real por quiebre de stock | Un hueco cuenta como espacio libre solo si mide al menos un ancho de producto. Es un criterio del equipo, y Walmart acepta cualquier criterio que se justifique ante el negocio (2026-09-16). El quiebre se informa para la góndola completa |

El plan de mejoras (`docs/plan-de-mejoras.md`, sección 4) los reformula
como cinco objetivos con meta medible. Su estado al 2026-10-20:

| Objetivo | Meta | Estado |
| --- | --- | --- |
| OE1. Segmentación de góndola y repisas | F1 ≥ 0,80 | Cumplido: F1 0,823 contra SHARD, en 1000 fotos no usadas para ajustar |
| OE2. Detección de productos | mAP50 ≥ 0,70 fuera de SKU-110K | En curso: 0,950 en el test de SKU-110K y 0,713 en 45 fotos de Kaggle; con la cámara a 35° baja a 0,637, así que se planificó un fine-tuning (#33) |
| OE3. % libre y alerta de la góndola completa | Diferencia con el % anotado (meta a fijar) | En curso: con productos envasados, alerta correcta en el 92% de 36 fotos y error medio de 6,2 puntos (#34) |
| OE4. App web con login por rol (CU00 a CU06) | 50% de los C.U para la Evaluación 2 | En curso: CU00, CU01, CU02 y CU06 operativos; CU03, CU04 y CU05 pendientes |
| OE5. Pruebas automatizadas y evaluación por lotes | CI en verde en cada PR | Cumplido: CI en cada PR; evaluación por lotes en `scripts/run_pipeline.py` |

**Objetivos y metodología ajustados.**

- **Metodología.** En la Fase 1 se planteó entrenar un modelo que
  reconociera los espacios vacíos. Se cambió por un método híbrido:
  OpenCV va primero (corrección y segmentación) y después un detector de
  productos. La justificación:
  - Los datasets públicos grandes anotan productos, no espacios vacíos.
  - Walmart prefiere un modelo que el equipo pueda explicar.
  - La segmentación clásica permite medir el espacio libre por repisa
    aunque la cámara esté en ángulo.
- **Entorno de entrenamiento.** Se entrena en una GPU local en vez de
  Google Colab.
- **Arquitectura web.** El diseño de la Fase 1 era una API REST con JWT y
  un frontend React. Se reemplazó por Django con sesiones (2026-10-18),
  porque Django ya trae login, roles, bcrypt, protección CSRF y
  migraciones probadas, y Walmart considera la interfaz opcional.
  Justificación completa en el README, "Estrategia Algorítmica y
  Arquitectura".
- **Alcance.** Tres cambios:
  - La ROI la segmenta el sistema y nadie la dibuja a mano (2026-09-27).
  - La profundidad de la góndola es una constante de 25 cm.
  - La alerta se informa para la góndola completa (pedido del profesor,
    2026-10-19).

**Evidencias de avance y cómo se resguardó la calidad.** El listado de
evidencias está en la sección 5 de `docs/plan-de-mejoras.md`. La calidad
se resguardó así:

- **Pruebas automatizadas:** 185 pruebas en 19 archivos con pytest,
  escritas antes del código en los módulos nuevos (TDD).
- **Integración continua:** GitHub Actions corre las pruebas y construye
  la imagen Docker en cada Pull Request, y `main` solo acepta cambios
  por PR con el CI en verde.
- **Medición contra datos anotados:** la segmentación se mide contra
  SHARD con una muestra de ajuste y otra de confirmación, y el detector
  contra el test de SKU-110K.
- **Plan de pruebas:** casos y resultados en `docs/test-plan.md`.
- **Licencias:** se revisan las de cada dataset; las fotos de SKU-110K
  no se muestran ni se modifican.
- **Auditoría de la app web** antes de publicarla, contra requisitos,
  casos de uso y mockups (`docs/auditoria-app-web.md`).

### A.2 Monitoreo del plan de trabajo

Competencias del perfil de egreso (las mismas de la guía 1.5):

- **C1.** Diseñar y generar soluciones de software innovadoras y de
  calidad, aplicando su ciclo de vida.
- **C2.** Evaluar y gestionar proyectos de su área durante todo su ciclo
  de vida.
- **C3.** Diseñar y adaptar los procesos de ingeniería de requisitos.

Estados de la guía 2.4: Completado, En curso, Con retraso, No iniciado,
Ajustada.

| Competencia | Actividad | Recursos | Duración | Responsable | Observaciones | Estado | Ajustes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C2 | Flujo de trabajo en equipo (ramas, PR, `PROGRESS.md`) | GitHub, Claude Code | 27-09 (1 día) | Francisco | Ordena el trabajo de 3 personas en paralelo | Completado | - |
| C2 | CI en GitHub Actions y protección de `main` | GitHub Actions, Docker | 27-09 (1 día) | Mariana | Desde el 2026-10-19 `main` no exige aprobación, pero sí PR y CI en verde | Completado | Aprobaciones requeridas: de 1 a 0 |
| C1 | Datasets: descarga reproducible, conversores y licencias | SKU-110K, SHARD, Kaggle, Roboflow, Hugging Face | 27-09 al 28-09 | Francisco, Mariana | 6 datasets; SKU-110K no se puede redistribuir ni mostrar | Completado | - |
| C1 | Plan de pruebas | pytest, `docs/test-plan.md` | 30-09 al 01-10 | Francisco | Primeros resultados por módulo | Completado | - |
| C1 | Corrección de imagen (dewarping y CLAHE) y recorte de ROI | OpenCV | 27-09 | Francisco | Sin calibración real de las cámaras de Walmart | Completado | La ROI es automática, no la dibuja un usuario |
| C1 | Segmentación automática de góndola y repisas | OpenCV, SHARD | 27-09 al 28-09 | Francisco | F1 de repisas 0,823 contra SHARD | Completado | - |
| C1 | Detector YOLO26: integración y entrenamiento | Ultralytics, GPU local de 8 GB, SKU-110K | 29-09 al 07-10 | Francisco | mAP50 0,950 en el test de SKU-110K | Completado | YOLO26 en vez de YOLOv8; GPU local en vez de Colab |
| C1 | Disponibilidad y alerta de quiebre (libre ≥ 30%) | Python | 30-09 | Francisco | - | Ajustada | Desde el 2026-10-19 se informa la góndola completa (#40) |
| C1 | Repisas inclinadas (niveles híbridos) | OpenCV, YOLO26 | 01-10 | Francisco | Para cámaras en ángulo | Completado | - |
| C1 | Pipeline completo, vista anotada y evaluación por lotes (CU07) | Python, Docker | 10-10 al 18-10 | Francisco | - | Completado | - |
| C3 | Quiebre por góndola completa (cambio de alcance) | - | 19-10 | Francisco | Pedido del profesor | Completado | - |
| C1 | Verificar el detector fuera de SKU-110K | Kaggle CC0, Roboflow | 20-10 al 21-10 | Francisco | mAP50 0,713 de frente; 0,637 a 35° | En curso | Fine-tuning planificado |
| C1 | Reportes Excel, CSV y PDF (CU04) | openpyxl, fpdf2 | 20-10 al 27-10 | Mariana | Fechas propuestas | No iniciado | - |
| C1 | Diseño, modelamiento y script de la base de datos | Django, SQLite | 18-10 al 19-10 | Francisco | Planificado en la Fase 1 para septiembre | Completado | Hecho con las migraciones de Django |
| C1 | Login, CRUD de usuarios y roles (CU00, CU06) | Django, bcrypt | 18-10 al 19-10 | Francisco | 22 pruebas de la app web | Completado | Django con sesiones en vez de API REST con JWT |
| C1 | Primer demo operativo ante Walmart | App web, pipeline | 27-10 al 31-10 | Nicko | Solo fotos que se pueden mostrar (no SKU-110K) | No iniciado | - |
| C1 | Instalación en el servidor del CITT | Imagen Docker | Por definir | Por definir | Faltan las instrucciones del CITT | No iniciado (bloqueado) | - |
| C3 | Registro de requisitos y plazos del curso | `docs/curso.md` | 09-10 al 10-10 | Francisco | - | Completado | - |
| C3 | Casos de uso y diagramas alineados con Walmart | Plantillas de C.U, Mermaid | 09-10 al 10-10 | Francisco | Adaptados a la app Django el 21-10 (#42, Mariana) | Completado | - |
| C2 | Plan de mejoras de la Fase 1 | `docs/plan-de-mejoras.md` | 20-10 | Mariana | Plazo 09-10 | Con retraso (terminado el 20-10) | - |
| C2 | Informe intermedio | Word | 19-10 al 21-10 | Francisco | Borrador en `Fase 2/`; entrega 21-10 | En curso | Antes era de Nicko; reasignado el 19-10 |
| C1 | Análisis de resultados: 10 mejores y 10 peores casos | Kaggle CC0, pipeline | 20-10 | Francisco | Alerta correcta en el 84% de 44 fotos | Completado | - |
| C2 | README completo | README.md | 20-10 | Francisco | Ejemplo reproducible | Completado | - |
| C2 | Video de demostración (5 a 10 min) | App web, fotos sin SKU-110K | 21-10 | Nicko | Entrega 21-10 | No iniciado | Antes era de Francisco; reasignado el 20-10 |
| C2 | Evidencias de avance (diario 2.1 y guía 2.4) | Este documento | 20-10 al 26-10 | Mariana | Faltan las plantillas oficiales | En curso | - |
| C2 | Feria de informática | - | Semana del 26-10 | Nicko | Día y hora por informar | No iniciado | - |

### A.3 Ajustes a partir del monitoreo

**Facilitadores.**

- **Datasets públicos con licencia académica:**
  - SKU-110K, para entrenar el detector.
  - SHARD, con las repisas anotadas, para medir la segmentación sin
    etiquetar a mano.
- **Integración continua:** detecta errores antes de que lleguen a
  `main`.
- **Asistentes de programación (Claude Code):** comparten reglas en
  `CLAUDE.md` y estado en `PROGRESS.md`, y siguen el mismo flujo de
  trabajo.
- **Reuniones con Walmart (03-09, 16-09 y 30-09):** dejaron criterios
  claros. Por ejemplo, que todo criterio del equipo vale si se justifica
  ante el negocio.

**Obstáculos.**

- **Walmart no comparte fotogramas de sus cámaras** ni el Dataset Oculto.
  No hay imágenes reales de cámara de sala para validar.
- **La licencia de SKU-110K** prohíbe mostrar o modificar sus fotos. Las
  demos y el análisis de casos tienen que usar otros datasets.
- **Cambios de alcance durante el semestre:** la ROI automática
  (27-09) y la alerta por góndola completa (19-10).
- **Entrenamiento en Windows con 8 GB de VRAM:** obligó a ajustar la
  configuración del entrenamiento (#18).
- **Servidor del CITT bloqueado:** todavía no llegan las instrucciones.
- **Semana del 12 al 16 de octubre sin commits de desarrollo.** Causa:
  **[A completar por el equipo]**.
- **Trabajo concentrado en un integrante:** 36 de los 40 Pull Requests
  mergeados vienen de una sola cuenta. La planilla de avance da 15
  puntos al aporte visible de cada integrante.

**Actividades ajustadas o eliminadas.**

| Actividad | Ajuste | Motivo |
| --- | --- | --- |
| Entrenar un modelo de espacios vacíos | Reemplazada por el detector de productos + segmentación clásica | Datasets disponibles y modelo explicable |
| Dashboard web en React y API REST con JWT | Reemplazada por la app Django con sesiones | Menos trabajo duplicado; la interfaz es opcional para Walmart |
| Editor manual de ROI (mockup Admin-1) | Eliminada | La ROI la segmenta el sistema |
| Alerta por repisa | Ajustada a góndola completa | Pedido del profesor (19-10) |
| Pruebas contra el Dataset Oculto | Ajustada: Walmart correría la imagen Docker en sus instalaciones y entregaría solo las métricas | Las imágenes no salen de Walmart; modalidad por confirmar (#24) |

**Actividades atrasadas o no iniciadas y su estrategia.**

| Actividad | Situación | Estrategia |
| --- | --- | --- |
| Plan de mejoras de la Fase 1 | Terminado el 20-10 (plazo 09-10) | Seguimiento de sus 10 mejoras en `docs/plan-de-mejoras.md` |
| Login y CRUD (pedidos para la semana 8) | Terminados el 19-10 | - |
| Verificar el detector fuera de SKU-110K | Medido: de frente cumple (mAP50 0,713); a 35° no (0,637) | Fine-tuning con Kaggle CC0 separado en entrenamiento y prueba, con aumentación de giros, color y ruido |
| Reportes (CU04) | No iniciado | Mariana, del 20 al 27-10, para la demo del 31-10 |
| Dashboard (CU03) y configuración (CU05) | No iniciados, sin responsable | Asignarlos en la próxima reunión del equipo. Con CU04 se llega al 50% de los C.U para la Evaluación 2 |
| Instalación en el CITT | Bloqueada | Imagen Docker lista; se instala cuando lleguen las instrucciones |
| Aporte equitativo en el repositorio | Desigual | Cada integrante abre los PR de sus ítems y revisa los de otro; `.mailmap` para unificar las identidades de autor (mejora M9) |

---

## Parte B. Diario de reflexión 2.1 (respuestas del grupo)

**1. ¿Se cumplió la Carta Gantt? ¿Qué lo facilitó o lo dificultó?**

Se cumplió en lo técnico y se atrasó en lo documental. Al 2026-10-20, la
Carta Gantt de la Fase 2 registra:

- 33 actividades cumplidas;
- 4 en curso;
- 7 pendientes;
- 1 bloqueada.

El pipeline de visión se terminó antes de lo planificado. Estas
actividades quedaron atrasadas:

- el plan de mejoras (plazo 09-10, terminado el 20-10);
- el Login y CRUD (pedidos para la semana 8, terminados el 19-10);
- la base de datos, planificada en septiembre y hecha el 18-10.

Facilitadores y obstáculos: ver A.3.

**2. ¿Cómo se enfrentaron las dificultades?**

- **Sin imágenes de Walmart:** se buscaron datasets públicos parecidos
  (SHARD, Kaggle, Roboflow) y se planificó generar vistas oblicuas
  sintéticas.
- **Licencia de SKU-110K:** solo se usa para entrenar y medir, nunca en
  demos.
- **Cambios de alcance:** se registraron en `docs/curso.md` y
  `PROGRESS.md`, y se implementaron como ítems separados.
- **Atrasos:** se reasignaron ítems, por ejemplo el informe intermedio el
  19-10.

**3. Autoevaluación del trabajo.** **[A completar por el equipo]**

**4. Dudas para el docente o los pares.** Las preguntas abiertas para el
profesor están en `docs/curso.md`. Por ejemplo:

- el día de la Evaluación 2;
- qué documentos se entregan el 26-10;
- si Django + SQLite cuenta como "estándar de la industria".

**[A completar por el equipo, si hay más]**

**5. ¿Hay que redistribuir actividades?** Sí. El desarrollo está
concentrado en Francisco. Propuesta del plan de mejoras (M9):

- Mariana toma los reportes (CU04, #7).
- Nicko, la demo (#29) y la feria (#38).
- Asignar el dashboard (CU03, #43) y la configuración (CU05, #44) a
  Mariana y Nicko.
- Cada integrante revisa los PR de otro.

**[A confirmar por el equipo]**

**6. Evaluación del trabajo en grupo.** **[A completar por el equipo]**
