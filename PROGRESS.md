# Bitácora de Sprint 1 - ShelfVision AI

El Sprint 1 cierra con la demo de la Evaluación 2 (Avance) de la Fase
2: semana del 2026-10-28, con el 50% de los C.U de la fase resueltos,
y debe servir como primer demo operativo ante Walmart (a más tardar
2026-10-31). Ver `docs/curso.md`.

Cada ítem tiene un número fijo (**#N**) que no cambia al reordenar: los
PR y otros documentos lo citan. Para tomar un ítem, agregar
`(dueño: <nombre>)` antes de empezar; al terminarlo, marcarlo `[x]` y
moverlo a "Hecho" en el mismo PR, editando solo las líneas de ese ítem
(ver "Trabajo en equipo" en `CLAUDE.md`).

## Estado actual

| Etapa | Estado | Ítems |
| --- | --- | --- |
| `src/preprocessing/` | Hecho: corrección de imagen, segmentación de góndola y recorte de ROI | #1, #2, #3, #4 |
| `src/models/` | Hecho: `ProductDetector` y detector `yolo26s` entrenado (mAP50-95 0.610 en test de SKU-110K; fuera de dominio, en Kaggle, mAP50 0.713 y R 0.644: falta fine-tuning) | #5, #33, #34 |
| `src/postprocessing/` | Hecho: disponibilidad medida a lo largo de cada repisa; se informan solo la alerta (libre >= 30%) y el % libre de la góndola completa | #6, #40 |
| `src/reporting/` | En desarrollo: vista anotada hecha (`annotate.py`); faltan los reportes Excel, CSV y PDF | #8, #7 |
| `scripts/run_pipeline.py` | Hecho: pipeline completo por foto, vista limpia, JSON y evaluación por lotes con IoU (CU07) | #8 |
| Datasets | 5 descargados y convertidos al estándar, con descarga reproducible | #10, #11, #12 |
| CI | Hecho: pytest + `docker build` en cada PR, `main` protegida | #13 |
| `web/` | Hecho: app web Django con login por perfil (CU00), usuarios y roles (CU06) y análisis de fotos (CU01) | #28 |

## Plan de trabajo por fases (2026-09-27)

1. [x] (dueño: Francisco) Terreno común: subir las ramas y abrir los PR
       #3, #4 y #5 (encadenados); flujo de trabajo en equipo en
       `CLAUDE.md`; `graphify-out/` fuera de git y regenerado
       localmente; setup de entorno nuevo en el README.
2. [x] (dueño: Mariana) CI con GitHub Actions (pytest + `docker build`)
       y protección de `main` (PR + revisión + CI en verde). Ítem #13.
3. [x] (dueño: Francisco) Buscar datasets que simulen cámaras de
       seguridad de sala. Candidatos registrados en `docs/datasets.md`
       (sección "Candidatos tipo cámara de sala"); descargarlos y
       evaluarlos sigue en el ítem #14.
4. [x] (dueño: Francisco) Recomendar skills de Claude Code aplicables
       al proyecto (`/skill-finder`). Recomendadas: plugins
       `yolo@ultralytics` (entrenamiento, tuning e inferencia de YOLO26)
       y `superpowers@superpowers-marketplace` (TDD, depuración
       sistemática, verificación antes de cerrar), más las ya incluidas
       `/code-review`, `/security-review`, `/simplify`, `xlsx`, `pdf` y
       `dataviz` (reportes, ítem #7). Los dos plugins quedan
       compartidos en `.claude/settings.json` (`extraKnownMarketplaces`
       + `enabledPlugins`): Claude Code los ofrece instalar al abrir el
       proyecto. Ojo: la skill
       `finishing-a-development-branch` de superpowers ofrece mergear
       localmente a `main`; elegir siempre la opción de Pull Request.
5. [x] (dueño: Francisco) Resolver limitaciones de la segmentación. Ítem
       #15: F1 de repisas en SHARD 0.758 -> 0.823 (holdout); lo que
       sigue, en #17.

## Pendientes (priorizados)

Los cuatro primeros responden al mensaje del profesor de la semana 8, y
los siguientes hasta el #39, al del 2026-10-16 (ver "Próximos
hitos" en `docs/curso.md`).

- [ ] **#27** Informe de estado de avance para el
      profesor, con los puntos que pidió su correo de la semana 7. Ya
      atrasado: el profesor lo está esperando. Ahora es el informe
      intermedio que pide el cliente, entrega 2026-10-21 (puntos en
      "Requisitos vigentes" de `docs/curso.md`). Formato Word, lo arma
      Francisco. Carta Gantt actualizada: `Anexos/Gestion/Carta Gantt
      Fase 2.xlsx` (copia de la Iteración 1, por semana, con estado de
      cada actividad; corte 2026-10-19). Las fechas de #7 y #37 son
      propuestas, a confirmar por sus dueñas. Puntos 2, 3 y 6 del
      informe salen de #35, #34 y #36. Avance (2026-10-20): borrador en
      `Fase 2/Informe intermedio de avance - ShelfVision AI.docx` con el
      formato de las pautas 2.2 y 2.3 (portada, índice, resumen y
      abstract, Calibri 11, número de página): estado por módulo y por
      C.U, Gantt, riesgos, próximos pasos, decisiones técnicas,
      datasets, métricas medidas, reproducibilidad, commits por
      integrante, conclusiones en inglés, bibliografía y anexo de PR.
      La sección 3 ya tiene los 20 casos con lámina y el análisis
      comparativo (#34). Falta (resaltado en amarillo en el Word): el
      enlace al video (#36) y las reflexiones individuales en inglés de
      cada integrante.
      Actualización (2026-10-20): README (#35) integrado, anexo de PR
      al día, video (#36) a cargo de Nicko y borrador de la reflexión de
      Francisco. Falta el enlace al video y las reflexiones de Nicko y
      Mariana (resaltadas en amarillo).
      Actualización (2026-10-21): reflexión de Mariana agregada y plan de
      mejoras (#26) corregido a cumplido (Tabla 11, resumen de la Gantt y
      retrasos). Falta el enlace al video y la reflexión de Nicko.
- [ ] **#29** Primer demo operativo ante Walmart, a más
      tardar 2026-10-31 (también se muestra en la Evaluación 2, semana
      del 2026-10-28): detector entrenado (#5), pipeline completo (#8)
      y reportes (#7), integrados con la aplicación web (#28). Para la
      demo, solo fotos que se pueden mostrar a terceros (no SKU-110K).
- [x] **#35** (dueño: Francisco) README completo para el informe intermedio (2026-10-21) y
      las evidencias de avance (2026-10-26): descripción de la solución,
      estrategia técnica y justificación de cada decisión (OpenCV antes
      de YOLO26, cabeza sin NMS, niveles híbridos, profundidad fija,
      umbral del 30%), diagramas de componentes y del flujo, datasets
      (origen, cantidad de imágenes, limpieza, etiquetado y
      preparación), estado operativo y pendiente, e instrucciones con
      un ejemplo para que un externo reproduzca la ejecución. Se cruza
      con #9. Hecho (2026-10-20): README con "La solución en
      breve", diagramas Mermaid del flujo y de los componentes, tabla de
      decisiones técnicas con su evidencia (incluye que las repisas son
      método de medición, no salida), tabla de datasets (origen, cantidad,
      limpieza, etiquetado y preparación), "Estado operativo y pendiente"
      y un ejemplo reproducible con fotos Kaggle CC0 (verificado: foto 026
      da 2% libre, sin alerta). Los pesos no se publican (licencia de
      SKU-110K): se piden al equipo o se entrenan con `docs/training.md`.
- [ ] **#36** Video de demostración de 5 a 10 minutos (entrega
      2026-10-21): solo funcionalidades implementadas y resultados que
      la aplicación genera hoy, con fotos que se pueden mostrar (no
      SKU-110K). El pipeline (#8) y la app web (#28) ya están en `main`.
- [ ] **#37** (dueño: Mariana) Evidencias de avance de la Fase 2, a más tardar
      2026-10-26: diario de reflexión 2.1, guía 2.4 (resumen del
      avance, plan de trabajo con estado y ajustes) e informe con el
      formato de las pautas 2.2 y 2.3 (abstract en español e inglés;
      conclusiones y reflexiones individuales en inglés). Todo en Git
      con la estructura y nombres pedidos; la planilla de avance da 15%
      al aporte de cada integrante visible en el repositorio. Detalle
      en "Requisitos vigentes" de `docs/curso.md`. Avance (2026-10-20):
      guía 2.4 llenada en su plantilla oficial (`Fase 2/2.4_GuiaEstudiante_Fase
      2_DesarrolloProyecto APT.docx`); contenido y borrador del diario 2.1
      en `docs/evidencias-avance.md`. Falta la plantilla 2.1 (no venía en
      el PR #42) y las partes de opinión del equipo (autoevaluación,
      evaluación del trabajo en grupo y causa de la semana del 12 al 16
      de octubre sin avances).
- [ ] **#38** Feria de informática (semana del 2026-10-26; día y hora
      por informar): definir qué integrante va (al menos uno) y qué se
      muestra.
- [ ] **#39** Instalar la aplicación en el servidor del CITT. Bloqueado:
      las instrucciones por sección llegan en los próximos días. Punto
      de partida: la imagen Docker que ya construye la CI (#13). Para la
      app web (#28): copiar los pesos `yolo26s` al volumen `/data`,
      configurar SMTP para los correos de CU06 y servir con HTTPS
      (cookies seguras). Hallazgos 15, 16 y 18 de
      `docs/auditoria-app-web.md`.
- [ ] **#42** Rehacer las plantillas de C.U, sus diagramas de secuencia
      y el diagrama de arquitectura según la app web Django (#28): sin
      API REST, JWT ni React; sesiones, formularios y plantillas HTML.
      Qué cambiar en cada uno: `docs/cambios-cu.md`. Hacerlo antes de
      las evidencias de avance (2026-10-26), donde se comparan diseño y
      sistema.
- [ ] **#43** Dashboard de disponibilidad (CU03, RF05): estado de cada
      góndola según su última foto (verde con menos de la mitad del
      umbral, amarillo hasta el umbral, rojo con alerta, "Sin datos" sin
      foto reciente) e historial de capturas. Con el pasillo y la
      góndola de cada análisis (#28) es una consulta por góndola.
      Hallazgo 12 de `docs/auditoria-app-web.md`.
- [ ] **#44** Configuración del umbral y de las cámaras (CU05, RF07):
      umbral de espacio libre entre 1% y 100% (hoy fijo en 30%,
      `AvailabilityParams.critical_free_fraction`) y cámaras asociadas a
      pasillo y góndola con su calibración de lente. Hallazgo 14.
- [ ] **#46** Falsas alertas en refrigeradores con puerta de vidrio
      (#34, fotos 020 y 003 de Kaggle): el reflejo y el desenfoque de la
      puerta en primer plano, los marcos entre puertas y una repisa en
      sombra cuentan como huecos. Propuesta: excluir zonas desenfocadas
      (nitidez local) y acotar la góndola a la parte enfocada; tratar los
      marcos de puerta. Es la condición más parecida a una cámara de sala
      que falla dentro del alcance.
- [ ] **#45** Privacidad de las fotos (RNF05): las fotos guardadas
      pueden mostrar clientes. Proponer a Walmart (#24) borrarlas tras N
      días o difuminar rostros antes de guardarlas. Hallazgo 17.
- [ ] **#48** Modelar el diagrama de la base de datos (entidad-relación) a partir de
      `web/models.py` (`User`, perfiles como grupos de Django, `Analysis`)
      y dejarlo en `Anexos/Diseño/Diagramas fuente (Mermaid)/` (`erDiagram`).
      Las filas de modelamiento de la Carta Gantt figuran cumplidas (#28)
      pero no hay diagrama. Incluir las tablas que traerían #43 y #44
      (cámaras, configuración) si se decide su diseño. Cruza con #42.
- [x] **#47** (dueño: Francisco) Auditoría de commits de GitHub: `.mailmap`
      que unifica las identidades (hoy 6 autores para 3 personas) y
      commits y PR sin la línea `Co-Authored-By` ni el pie de Claude
      Code. Los commits ya publicados no se reescriben (regla 5).
- [ ] **#7** Implementar generación de reportes (Excel, CSV, PDF) en
      `src/reporting/`. Contenido mínimo (#30, acuerdos con Walmart en el
      README): % libre de la góndola completa (#40) y alerta sí/no; así sirve
      para cualquiera de las dos lecturas del umbral (#24). Walmart no
      pide un formato: dejar en el README por qué se eligieron estos.
- [ ] **#33** Verificar el detector `yolo26s` fuera de SKU-110K, en las
      condiciones con que evaluará Walmart (IoU contra anotación a mano;
      fotos frontales, en ángulo y desde arriba). Hoy solo está medido en
      el test de SKU-110K, que es igual al entrenamiento. Depende del modo
      por lotes de #8 (CU07). Con datos ya descargados:
      (1) Kaggle supermarket-shelves (45 fotos con productos anotados,
      CC0, no usadas al entrenar): P, R, mAP50 y mAP50-95;
      (2) las mismas fotos giradas con `oblique_view()` a 20° y 35° (#22);
      (3) Roboflow Out Of Stock y Empty Shelf (espacios vacíos anotados):
      IoU entre los huecos de `compute_availability()` y los vacíos
      anotados; (4) revisión a ojo de botellas y envases cilíndricos
      frente a cajas (los datos no etiquetan la forma). Después, el set
      propio de #32. Criterio: reentrenar (fine-tuning con Kaggle CC0,
      fotos propias y aumentación de giros chicos, color y ruido) solo si
      alguna medición queda bajo mAP50 0.70 (referencia de Walmart: con
      ~70% el problema está casi resuelto); nunca generar imágenes
      sintéticas desde SKU-110K (licencia). Primera prueba de humo con #8
      (2026-10-10, 6 fotos de Kaggle, ver `docs/test-plan.md`): R 0.425
      por la foto 030 (verduras sueltas, fuera del alcance: 21 de 546);
      sin ella, R 0.70. Falsa alerta en la 020 (refrigeradores llenos,
      34% libre contra 11% de la anotación): los marcos entre puertas,
      letreros y vidrio borroso cuentan como huecos de al menos un ancho
      de producto (criterio de #6). Registrar los resultados en
      `docs/test-plan.md` (#19). Paso (1) hecho en #34 (2026-10-20, 45
      fotos): mAP50 0.713 (justo sobre 0.70), mAP50-95 0.423, R 0.644;
      el recall en envasados (0.71) causa casi todas las falsas alertas,
      así que se recomienda el fine-tuning aunque el mAP50 pase el
      criterio. Las 45 fotos ya se usaron para evaluar: para afinar con
      ellas, separar entrenamiento y prueba. Pasos (2) y (3) hechos (2026-10-20, detalle en el registro de
      `docs/test-plan.md`): Kaggle girado, mAP50 0.704 de frente, 0.688 a
      20° y **0.637 a 35°** (bajo el criterio 0.70; mAP50-95 de 0.41 a 0.21:
      se pierde la localización, no el recall). Roboflow Out Of Stock
      (200 fotos): IoU de huecos 0.106, 24 falsas alertas y 2 quiebres
      (2 detectados); Empty Shelf (60): IoU 0.162, 3 falsas alertas. Sus
      espacios vacíos son chicos y no comparables con huecos de un ancho
      de producto. Con 35° se cumple el criterio: toca el fine-tuning
      (Kaggle CC0 separado en entrenamiento y prueba, aumentación de giros,
      color y ruido). Paso (4) hecho (2026-10-20, a ojo y con las métricas por foto de
      #34): de frente, las botellas (026, R 1.00) y las latas y potes
      (R 0.93 a 0.98) se detectan igual de bien que las cajas (017, R
      0.94); el IoU de las latas es menor (0.72 a 0.77 contra 0.89) por
      cómo se cortan las pilas. El único fallo claro (028, R 0.27) es
      oclusión y ángulo, no la forma. Los envasados con recall bajo son
      botellas chicas y lejanas (013, 022), lácteos (032) y el
      refrigerador (020). Pendiente: el set propio (#32) y el
      fine-tuning, que no es urgente (se dejó para cuando el PC esté
      libre). Plan, ya probado hasta el arranque: Kaggle CC0 sin las 8
      fotos de frutas y verduras sueltas (005, 007, 014, 023, 029, 030,
      033, 034), separado por foto en 24 de entrenamiento y 12 de prueba
      (001, 004, 009, 012, 016, 019, 022, 026, 031, 037, 040, 043);
      entrenamiento con las 24 más sus vistas giradas a 20° y 35° (15°
      hacia abajo, `oblique_view()`) y 300 fotos de SKU-110K `train` para
      no olvidar; desde `yolo26s/weights/best.pt`, 30 épocas, SGD lr0
      0.002, `imgsz=1280`, batch 2, `nms=False`, `max_det=1000`, giro 3°,
      perspectiva 0.0005, saturación 0.7. Reducir las fotos de Kaggle a
      2560 px de lado mayor antes: a tamaño completo (5616 x 3744) la
      carga de datos da ~10 s por iteración; reducidas, ~4 s (unos 12 min
      por época con 2 procesos de carga). Línea base en las 12 fotos de
      prueba (`yolo26s` actual), mAP50 / mAP50-95: de frente 0.809 /
      0.481; 20° 0.781 / 0.334; 35° 0.703 / 0.217. Aceptar el modelo
      nuevo solo si mejora esas cifras y no baja el mAP50-95 de 0.610 en
      el `test` de SKU-110K; con 12 fotos de prueba, el resultado es
      orientativo hasta tener el set propio (#32).
- [ ] **#31** Excluir de la medición la bodega de reserva que hay sobre
      la góndola de venta (Walmart no la evalúa; acuerdo del 2026-09-16
      en el README). Hoy `compute_availability()` acota la góndola "del
      primer al último nivel con productos", y las cajas de la bodega
      cuentan como productos: sus huecos pueden disparar alertas falsas.
      Opciones: descartar el nivel sobre la última repisa de venta, o
      cortar por altura en la imagen. Las islas del pasillo tampoco se
      miden (ya quedó en el README).
- [ ] **#32** Fotos propias de góndolas en tienda (con permiso),
      clasificadas por ángulo (frontal, lateral, desde arriba, gran
      angular), y un set chico anotado a mano en el formato estándar.
      Las pide el acta de la primera reunión con Walmart y sirven para:
      (1) medir IoU contra anotación a mano, como evaluará Walmart
      (agregarlo a `docs/test-plan.md`, #19); (2) control con ángulo real,
      que #22 no tiene; (3) demos sin SKU-110K. Probar CU07 con este set.
- [ ] **#9** Documentar especificaciones técnicas y diagramas en `docs/`.
- [ ] **#14** Datasets con imágenes tipo cámara de seguridad (vista alta,
      oblicua, gran angular/fisheye, pasillo completo) para validar
      dewarping y segmentación en condiciones parecidas a Walmart.
      Candidatos en `docs/datasets.md` ("Candidatos tipo cámara de
      sala"): ninguno público combina cámara de sala real con anotación
      de productos. Siguientes pasos: (1) descargar SHARD; (2) pedir
      MMPTrack (entorno *retail*, cámaras fijas calibradas); (3) generar
      imágenes "tipo CCTV" sintéticas a partir de SHARD y Kaggle (no de
      SKU-110K: su licencia prohíbe modificar sus fotos)
      (distorsión fisheye con `LensCalibration`, homografía oblicua,
      baja resolución, compresión JPEG, ruido), transformando también
      sus anotaciones. Walmart no comparte fotogramas reales de sus
      cámaras (#21), así que el paso (3) es ahora el principal sustituto
      de la cámara de sala y sube de prioridad.
- [ ] **#17** Limitaciones de la segmentación que siguen tras #15 (F1
      de repisas 0.82 en SHARD):
      - Líneas sobre filas de productos iguales (bandas de color o
        bordes superiores alineados de bolsas y cajas apiladas): los
        chequeos clásicos probados en #15 no las separan de las
        repisas. Atacarlas en `src/postprocessing/` con el detector
        (#5): una línea que cruza por el medio de productos detectados
        no es repisa.
      - Recall 0.85: el soporte de borde descarta repisas reales tapadas
        en parte (postes, productos colgantes).
      - Localización: la diferencia con la altura anotada en SHARD está
        centrada (mediana +0.5% del alto) pero dispersa (desv. estándar
        2%), por el grosor del borde de repisa y el ruido de anotación;
        con tolerancia 5% el F1 es 0.88.
      - Fotos con perspectiva fuerte y primeros planos de productos
        colgantes (sin repisas).
      - ROI casi igual a la imagen en primeros planos y validación con
        cámaras de sala: siguen en #14. Para lo que SHARD no cubre
        (repisas inclinadas, contorno de la góndola), set chico
        etiquetado a mano (polilíneas, ej. en CVAT o Label Studio).
- [ ] **#24** Preguntas para la próxima reunión con
      Walmart (fecha: por definir). Hasta ahora no han dicho nada de sus
      cámaras, y del Dataset Oculto probablemente no puedan decir nada
      (#21):
      - ¿Aceptan correr el sistema (imagen Docker) en sus instalaciones
        con el Dataset Oculto y entregarnos solo las métricas?
      - Si no pueden mostrar el Dataset Oculto, ¿pueden describirlo sin
        imágenes (cantidad de fotos, tipo de góndolas, condiciones)?
      - Cámaras: modelo de cámara y lente, campo de visión, altura y
        ángulo de montaje, resolución y compresión de los fotogramas.
      - ¿Tienen parámetros de calibración de lente (ej. con tablero de
        ajedrez)? Los usaría `LensCalibration` (#3).
      - Umbral: el acta de la primera reunión dice "menos del 30% de
        productos disponibles", y el sistema alerta con espacio libre
        >= 30%. ¿Cuál de las dos lecturas quieren? (#30)
      - Alcance: la primera reunión propuso pan y pollo "en principio".
        ¿Aceptan no perecibles?
      - Medidas estándar de la góndola que iban a enviar (profundidad,
        alto y ancho de módulo). El ancho de módulo daría la escala cm/px
        del Nivel 1.
      - Su IoU, ¿se mide sobre los productos o sobre los espacios vacíos?
      - El par de imágenes de ejemplo difíciles que ofrecieron.
      - ¿Qué hito es "antes del 18" (mencionado en la reunión del
        2026-09-30)?

## Hecho

- [x] **#34** (dueño: Francisco) Análisis de resultados del informe
      intermedio (2026-10-20), en `docs/analisis-resultados.md` y la
      sección 3 del informe (#27). Pipeline completo en CPU sobre las 45
      fotos de Kaggle (CC0, no usadas al entrenar) con su anotación
      (`run_pipeline.py --annotations`); el resultado esperado es la
      anotación medida con el mismo pipeline (`measure_boxes()`). 10
      mejores y 10 peores casos con lámina (entrada | sistema |
      esperado) en `docs/analisis-resultados/`, causa y propuesta.
      Detector (Ultralytics `val`): P 0.843, R 0.644, mAP50 0.713,
      mAP50-95 0.423 (en test de SKU-110K, 0.950 / 0.610). Sistema, 44
      fotos únicas (la 035 repite la 004): P 0.889, R 0.555, alerta
      correcta 84%, error medio de % libre 9.6 pts; envasados (36): P
      0.900, R 0.713, alerta 92%, 6.2 pts; frutas y verduras sueltas (8,
      fuera del alcance): R 0.156, 4 de las 6 falsas alertas. Mediana de
      0.51 s por foto. Patrones: el recall fuera de dominio crea huecos
      falsos (6 de 7 errores de alerta son falsas alertas); vidrio,
      sombra y desenfoque en refrigeradores (#46); pocos productos por
      repisa (011, el único quiebre real del set, queda 3 puntos bajo el
      umbral). Acciones: fine-tuning (#33), declarar fuera del alcance lo
      que va a granel (#24), #46 y medir quiebres reales (Roboflow, #32).
- [x] **#28** (dueño: Francisco) Aplicación web mínima en `web/`
      (Django 6.1 + SQLite; stack elegido el 2026-10-18 con un consejo
      de 5 perspectivas: Django trae login, roles, bcrypt, CSRF, ORM y
      migraciones probados, y React duplicaba el trabajo para una
      interfaz que Walmart considera opcional; justificación en el
      README, "Estrategia Algorítmica y Arquitectura"). CU00: login con
      RUT o correo, vista principal por perfil (Administrador ->
      Usuarios, Jefe de Salón -> Análisis, Reponedor -> Alertas) y
      bloqueo tras 5 intentos fallidos. CU06: el Administrador crea y
      edita usuarios con rol y estado; la contraseña la define el
      usuario con un enlace de un solo uso (sin contraseñas por correo)
      y desactivar una cuenta cierra sus sesiones. Los usuarios se
      desactivan, no se borran. CU01 desde la web: subir una foto,
      correr `run_image()` y guardar en la base el % libre de la góndola
      completa, la alerta y la foto anotada (solo visible con sesión).
      Imagen Docker con gunicorn (1 worker: cada uno cargaría su copia
      de YOLO26) y volumen `/data` para la base, las fotos y los pesos.
      Tests: 10 en `tests/test_web.py` (pytest-django); suite completa
      203 OK. Prueba manual de punta a punta con YOLO real (pesos
      `smoke`, foto Kaggle 039): login, crear usuario, análisis en
      7,4 s con la carga del modelo. Auditoría antes de publicar
      (2026-10-19, `docs/auditoria-app-web.md`, contra RF, RNF, CU y
      mockups) y rediseño con las skills `design-taste-frontend` e
      `impeccable` (contexto en `PRODUCT.md`, sistema en `DESIGN.md`):
      mundo "fleje de góndola" elegido por el usuario entre 6
      direcciones (cada góndola dibujada como sus repisas, con los
      huecos en su posición real), estilos, fuente e íconos servidos
      desde la app sin CDN (whitenoise). P0 resueltos: pasillo y
      góndola al subir la foto; ciclo de la alerta (Activa, En proceso
      con quién y desde cuándo, Completada; una foto nueva reemplaza la
      alerta abierta o confirma la reposición); vista de alertas para
      el teléfono con recarga cada minuto; estados vacíos y páginas
      403/404/500; sesión que expira tras 2 h sin uso; foto de hasta
      20 MB; dígito verificador del RUT; el Administrador no puede
      desactivarse; el modelo se precarga al arrancar el servidor.
      Adaptado al alcance por góndola completa (#40, 2026-10-19): el
      fleje muestra solo la geometría de los huecos, sin % ni quiebre
      por repisa. Tests: 22 en `tests/test_web.py`. Pendiente: confirmar con el
      profesor que Django + SQLite cuenta como "estándar de la
      industria" y CU06 como implementado; los P1 de la auditoría
      quedan en #7, #39, #43, #44 y #45.
- [x] **#1** (dueño: Francisco) Implementar
      `src/preprocessing/roi_filter.py`: recortador de región de interés
      (ROI) sobre la góndola detectada, incluyendo normalización de
      coordenadas `[x_min, y_min, x_max, y_max]`. API: `normalize_roi()`
      (ordena, redondea hacia afuera, recorta a la imagen), `crop_roi()`
      -> `RoiCrop` (copia del recorte + ROI usada) y
      `RoiCrop.to_original()` para devolver detecciones del recorte a
      coordenadas de la imagen original. ROI parcialmente fuera se
      recorta; totalmente fuera, imagen None o vacía -> `ValueError`. La
      ROI llega como parámetro; la entrega la segmentación automática de
      la góndola (ítem #4).
- [x] **#2** (dueño: Francisco) Implementar pruebas unitarias en
      `tests/test_preprocessing.py` para `roi_filter.py` (casos: ROI
      dentro de límites, ROI fuera de límites, imagen vacía/None) — 16
      tests, suite completa 24/24 OK.
- [x] **#3** (dueño: Francisco) Implementar filtros CLAHE y dewarping en
      `src/preprocessing/`: `image_correction.py` con `correct_image()`
      (dewarping y luego CLAHE) -> `CorrectedImage` (imagen +
      calibración usada, con `to_original()`/`to_original_points()` para
      devolver detecciones a coordenadas de la imagen original).
      `dewarp()` corrige solo la distorsión de lente (modelo pinhole o
      fisheye de OpenCV) y conserva el tamaño y la matriz de cámara.
      `apply_clahe()` ecualiza solo la luminancia (Lab) para no alterar
      colores. `LensCalibration.approximate(k1)` da una calibración
      genérica mientras no existan las reales. 21 tests en
      `tests/test_image_correction.py` (entre ellos, una repisa curvada
      con distorsión sintética que vuelve a quedar recta). Validaciones
      de imagen compartidas en `_validation.py`. Pendiente: pedir a
      Walmart el modelo de cámara y lente, o los parámetros de
      calibración si ellos calibran con un tablero de ajedrez (no
      comparten imágenes de sus cámaras, #21). Los datasets públicos no traen
      distorsión de lente: con ellos se usa solo CLAHE (sin
      calibración).
- [x] **#4** (dueño: Francisco) Implementar la segmentación automática
      de la góndola y sus repisas en `src/preprocessing/` (cambio de
      alcance 2026-09-27: ningún usuario define la ROI). Visión clásica,
      antes de YOLO26. Hecho: `gondola_segmentation.py` con
      `segment_gondola()` -> `GondolaSegmentation` (ROI, `ShelfLine` por
      repisa, bbox por nivel y `found`). Método: saltos del brillo
      promedio por fila en franjas verticales, enlazados entre franjas
      (permite repisas inclinadas por perspectiva). Se descartó Canny +
      Hough: el texto de las etiquetas dominaba y cada fila de cajas
      salía como repisa. Sin repisas detectadas -> imagen completa con
      `found=False` (contingencia de análisis global). Visor:
      `scripts/visualize_segmentation.py` (láminas + `metrics.csv` en
      `data/processed/segmentation_preview/`). Métricas aproximadas en
      `src/evaluation/segmentation_proxy.py`, que usan las anotaciones
      existentes como evidencia indirecta. Línea base (100 imágenes por
      dataset): 99-100% de las anotaciones (incluidos los espacios
      vacíos) quedan dentro de la ROI; en SKU-110K la ROI ocupa el 91%
      del área, el 52% de los productos queda apoyado sobre una repisa
      detectada y el 76% de las repisas detectadas tiene productos
      encima. La métrica de repisas con productos subestima: el borde
      superior de la góndola y las repisas vacías son líneas correctas
      sin productos encima. Limitaciones conocidas y cómo atacarlas: ver
      ítem #15. Pendientes: set de validación con góndolas/repisas, y
      evaluarlo en condiciones de cámara de sala (imágenes sintéticas,
      #14; Walmart no comparte imágenes reales, #21).
      Especificación original: debe entregar la ROI de la góndola
      (entrada de `crop_roi()`) y, para el Nivel 1, los límites de cada
      repisa. Corre después de `correct_image()`, sobre la imagen
      corregida (decidido 2026-09-27: con lente fisheye las líneas de
      repisa se ven curvas). La corrección de perspectiva por ángulo
      oblicuo (llevar el contorno de la góndola a un rectángulo) va
      aquí, porque necesita ese contorno; `image_correction.py` no la
      hace.
- [x] **#5** (dueño: Francisco) Integrar inferencia YOLO26 en `src/models/` (se decidió
      YOLO26 sobre YOLOv8/YOLO11 por su cabeza sin NMS y mejor manejo de
      objetos chicos, clave en productos apilados). Validado en local:
      `ultralytics` 8.4.164 + `yolo26n.pt` corre sobre SKU-110K y se
      encadena con `crop_roi()`/`to_original()`; `tests/test_models.py`
      fija el contrato (versión >= 8.4.0, `nms=False` activa el modo
      end-to-end y respeta `max_det`). Hecho (2026-09-29): inferencia en
      `src/models/detector.py` (`ProductDetector.detect()` -> lista de
      `Detection` con bbox estándar, fija `nms=False`, `max_det=1000` e
      `imgsz=1280`, y rechaza modelos sin cabeza sin NMS). Dataset YOLO con
      `scripts/prepare_yolo_dataset.py` (`xyxy_to_yolo()` en
      `converters.py`). Las imágenes se enlazan desde `data/raw/`; los 712
      JPEG truncados de SKU-110K se copian, porque Ultralytics los
      reescribe al repararlos. Entrenamiento, reanudación y evaluación en
      `scripts/train_detector.py` (variantes `yolo26s` y `yolo26s-p2`,
      entrena y valida con `nms=False` y `max_det=1000`: por defecto
      Ultralytics mide la cabeza con NMS y corta en 300 cajas). Guía para
      el PC con GPU en `docs/training.md`. Todo el flujo verificado con
      una prueba corta en CPU (16 imágenes, 1 época). Para 8 GB bajo
      Windows (2026-10-01): límite de VRAM con asignador en CPU ante OOM
      (`src/models/vram.py`), EcoQoS desactivado (`src/models/power.py`) y
      `resume --batch`.
      Entrenado (2026-09-30 a 2026-10-07) en RTX 5060 8 GB, 50 épocas,
      `imgsz=1280`, SKU-110K (mejor época de ambas: 40):

      | Variante | Batch | Tiempo aprox. | P | R | mAP50 | mAP50-95 |
      | --- | --- | --- | --- | --- | --- | --- |
      | `yolo26s` (val) | 2 | ~7,5 h (~9 min/época) | 0.915 | 0.884 | 0.947 | **0.606** |
      | `yolo26s-p2` (val) | 1 | ~17 h (~20 min/época, 6 tramos) | 0.910 | 0.879 | 0.941 | 0.596 |
      | `yolo26s` (test, 2.935 imágenes) | 2 | - | 0.915 | 0.885 | 0.950 | **0.610** |

      Ganadora: `yolo26s` (mejor mAP50-95 y recall en val; la cabeza P2,
      pensada para objetos chicos, no mejora en SKU-110K y cuesta el doble).
      Inferencia en GPU: ~15 ms por imagen a 1280. Los pesos (`best.pt`) se
      comparten solo con el equipo (Drive/OneDrive), no en git: uso
      académico y no comercial por venir de SKU-110K.
- [x] **#15** (dueño: Francisco) Limitaciones de la segmentación (ítem
      #4), medidas contra las repisas anotadas de SHARD. Hecho: SHARD en
      el catálogo (`shard`: figshare, CC BY 4.0, `.7z` de 3.6 GB que se
      descomprime con `py7zr`, más `annotation.csv`; 22,743 fotos
      verificadas con `--check` y MD5 de figshare). Evaluador
      `src/evaluation/shelf_evaluation.py`: cada `ShelfLine` se reduce a
      su Y promedio (en una recta, la Y en el centro del tramo) como
      fracción del alto y se empareja 1 a 1 con las repisas anotadas con
      tolerancia configurable (3% del alto por defecto); precisión,
      recall y F1 por imagen y en total. CLI `scripts/evaluate_shard.py`
      (fotos barajadas con semilla 0: "dev" = primeras 1000, para
      ajustar; "holdout" = siguientes 1000, para confirmar) y
      `visualize_segmentation.py --dataset shard` (lámina con las
      repisas anotadas en verde). Resultados con tolerancia 3%
      (precisión / recall / F1):
      línea base dev 0.661 / 0.888 / 0.758, holdout 0.660 / 0.890 /
      0.758; final dev 0.793 / 0.851 / 0.821, holdout 0.796 / 0.851 /
      0.823. Cambios adoptados, medidos uno a uno en dev:
      (1) soporte de borde a lo largo de toda la recta (subfranjas de
      1/4 de franja; el 70% debe tener un salto de al menos 0.5 veces
      la referencia de su franja): F1 0.758 -> 0.796, elimina la mayoría
      de las diagonales falsas; (2) un borde a menos de la separación
      mínima entre repisas (7% del alto) del borde superior de la foto
      no se informa como repisa (sin espacio para productos encima;
      SHARD anota ahí el 0.1% de sus repisas y el método ponía 536
      líneas en 1000 fotos, ~1% correctas), pero sigue limitando la ROI:
      -> 0.821; (3) la ROI se extiende de a una franja hacia los lados
      mientras haya textura (antes era la unión de los tramos de las
      líneas y, con menos líneas, quedaba a media imagen): no cambia el
      F1 y mantiene las anotaciones dentro de la ROI en 0.99-1.00.
      Descartados porque bajan el F1: coherencia de la pendiente con las
      repisas vecinas (ajuste ángulo vs. altura; con umbral de 1-3°, F1
      0.695-0.790: las pendientes ajustadas con 6 puntos son ruidosas),
      patrón de franja de repisa (dos bordes cercanos de signo opuesto:
      no separa repisas de filas de productos, AUC 0.50; uniformidad y
      saturación de la franja: AUC 0.62-0.67, todo umbral baja el F1),
      más franjas, menor `min_edge` y menor separación mínima. Métricas
      aproximadas en los otros 5 datasets (100 fotos c/u): anotaciones
      dentro de la ROI y área de la ROI sin cambios; repisas con
      productos encima sube (SKU-110K 0.76 -> 0.80) y productos
      apoyados en una repisa baja (0.52 -> 0.48), coherente con más
      precisión y algo menos de recall. Una foto de Out Of Stock (de
      100) queda sin repisas (`found=False`, contingencia de análisis
      global). Lo que sigue: ítem #17.
- [x] **#6** (dueño: Francisco) Cálculo de disponibilidad y alerta de
      quiebre de stock en `src/postprocessing/availability.py`:
      `compute_availability(productos, niveles)` ->
      `GondolaAvailability` (espacio libre de la góndola, alerta y
      `ShelfAvailability` por repisa con sus huecos, área libre en px y
      `level_index`) y `free_volume_cm3()` (área libre x 25 cm, cuando
      haya escala cm/px). Recibe cajas y niveles como tuplas o arrays
      (no importa `src/preprocessing` ni `src/models`); sin repisas, la
      ROI es el único nivel. Criterio (decidido 2026-09-30, reemplaza
      "disponibilidad < 30%", que leído al pie de la letra alertaba con la
      góndola llena): alerta si el espacio **libre** es >= 30% del
      frente de la góndola. Métrica: cobertura horizontal por repisa;
      hueco = tramo sin producto de al menos 1 ancho de producto (mediana
      de la repisa). No mide la altura de los productos: pilas con pocas
      unidades o productos bajos siguen disponibles, y el eje vertical es
      el que más deforma una cámara de sala. Una caja cubre todo nivel
      con el que comparte >= 30% del alto menor, así una repisa falsa a
      media altura de una fila de productos (#17) no crea un nivel vacío.
      La góndola se acota a los productos (del primer al último nivel con
      productos, y del producto más a la izquierda al más a la derecha):
      la ROI de la segmentación incluye pasillo, techo y carteles. Medido
      con `scripts/evaluate_availability.py` (SKU-110K `val`, 300 fotos,
      anotaciones como detector y recall simulado 0.9): falsas alertas
      con la góndola llena 24.7% con la ROI -> 4.0% acotada; quiebre
      simulado en el interior de 30% del frente detectado 87%, de 40%
      99.7%. Umbral: 20% / 25% / 30% / 35% dan 20.7% / 8.7% / 4.0% / 1.0%
      de falsas alertas; se mantiene 30%. Costo del acotado: una repisa
      extrema vacía entera, o una franja vacía en todas las repisas en un
      extremo, no se cuentan (quiebre de 40% en cualquier parte: 88%).
      24 tests en `tests/test_availability.py`. Pendiente: medir con el
      detector entrenado (#5) y con fotos de cámaras de sala (#14).
- [x] **#10** (dueño: Francisco) Descargar datasets candidatos (ver
      `docs/datasets.md`): SKU-110K, grocery-shelves (UniDataPro),
      supermarket-shelves (Kaggle), Out Of Stock detection y Empty Shelf
      Detector (Roboflow) — los 5 ya están en `data/raw/`.
- [x] **#11** (dueño: Francisco) Escribir conversores de anotaciones a
      nuestro estándar `[x_min, y_min, x_max, y_max]`: lógica pura en
      `src/datasets/converters.py` (probada en
      `tests/test_dataset_converters.py`, 8/8 tests OK) + CLI
      `scripts/prepare_datasets.py` que recorre `data/raw/` y escribe
      `data/processed/annotations/<dataset>.csv` + `all_annotations.csv`
      (1,760,633 anotaciones combinadas de los 5 datasets). No
      versionado (`data/processed/*` en `.gitignore`).
- [x] **#12** (dueño: Francisco) Script de descarga reproducible:
      `scripts/download_datasets.py` (`--list`, `--check`, `--dataset`,
      `--force`, `--keep-archives`) con el catálogo en
      `src/datasets/sources.py` (URLs y versiones fijas, licencia, si se
      puede compartir y cantidad de archivos esperada por dataset).
      SKU-110K y Kaggle bajan como archivo comprimido (SKU-110K con
      tamaño verificado y descarga reanudable), UniDataPro archivo por
      archivo desde Hugging Face, y Roboflow por su API con
      `ROBOFLOW_API_KEY`. Extracción protegida contra rutas que escapan
      de la carpeta; el zip de Kaggle trae una carpeta raíz extra que
      se quita (`archive_root`). 17 tests en
      `tests/test_dataset_sources.py`. Verificado: `--check` valida los
      5 datasets locales; descarga real de UniDataPro y Kaggle idéntica
      a la copia local, y reanudación real de una descarga cortada. Sin
      probar: la descarga de Roboflow (nadie tiene API key aún) y la
      de SKU-110K completa (solo URL y reanudación).
- [x] **#13** (dueño: Mariana) CI en GitHub Actions: correr
      `pytest tests/` y `docker build` en cada PR, y proteger `main`
      (merge solo por PR con una revisión y CI en verde). Hecho:
      `.github/workflows/ci.yml` con los jobs `tests` (Python 3.10,
      PyTorch CPU) y `docker` (build sin publicar + pytest dentro de la
      imagen), en `ubuntu-24.04` fijo (`ubuntu-latest` pasa a Ubuntu 26
      el 2026-10-19 y puede no traer Python 3.10). Protección de `main`
      aplicada: PR obligatorio, 1 aprobación, checks `tests` y `docker`,
      también para admins, sin force push ni borrado.
- [x] **#16** (dueño: Mariana) Corregir datos desactualizados de
      `docs/datasets.md` (licencias, tamaño de grocery-shelves y estado
      de descarga). Licencias: supermarket-shelves es CC0 1.0 y los dos
      de Roboflow CC BY 4.0, igual que `src/datasets/sources.py`;
      grocery-shelves ocupa ~37 MB en disco (no 71 MB); el estado de
      los 5 indica su clave en `scripts/download_datasets.py`.
- [x] **#18** (dueño: Francisco) Notas de instalación en un entorno
      nuevo (Windows): README explica cómo detectar una copia vieja de
      `graphify` que tapa la 0.9.70 en el `PATH`, y que SKU-110K y SHARD
      se reanudan volviendo a correr el script si la descarga se corta;
      `docs/datasets.md` explica la descarga manual de los 2 datasets
      de Roboflow (sin API key) y dónde descomprimirlos.
- [x] **#19** (dueño: Francisco) Plan de pruebas en `docs/test-plan.md`:
      para cada etapa ya hecha, qué requisito cumple, cómo se prueba,
      criterio de aceptación y resultado actual; trazabilidad con
      RF01-RF05 y lo que aún no se puede probar. Primera ejecución
      completa tras mergear #6 (2026-09-30, `main` 9cd8286): 131 tests
      OK; SEG-02 F1 0.823, SEG-03 0.99-1.00, AV-02 4.0% y AV-03 99.7%,
      todo dentro de criterio (detalle en el registro del plan).
      Volver a ejecutarlo con el detector entrenado (#5) y con el
      pipeline completo (#8).
- [x] **#22** (dueño: Francisco) Repisas inclinadas (fotos en ángulo
      o cámara de sala). Problema: con perspectiva, `segment_gondola()`
      pierde repisas (acepta 8° de inclinación como máximo y en vista
      oblicua cada repisa da varios bordes: superficie, borde frontal y
      sombra) y sus niveles son rectángulos horizontales que se meten en
      los niveles vecinos: los productos de una repisa tapan los huecos
      de otra y aparecen huecos falsos. Hecho: `src/postprocessing/
      shelf_levels.py` con `shelf_levels(productos, líneas de la
      segmentación, ROI)` -> niveles como franjas inclinadas
      (cuadriláteros de lados verticales), y `compute_availability()`
      acepta esas franjas además de los bbox (cobertura medida a lo largo
      de la repisa). Repisas = (1) filas de productos: rectas por las
      bases de al menos 3 productos (búsqueda tipo Hough en la pendiente,
      hasta 35°), descartando las que cruzan productos por la mitad, las
      capas de una pila (la mayoría de sus productos apoyados directo
      sobre otro, sin borde de repisa) y las que no calzan con un mismo
      punto de fuga (pendiente lineal en la altura; tolerancia 3°); más
      (2) las líneas de la segmentación que no cruzan productos (ataca la
      primera limitación de #17) ni quedan a menos del 40% de la
      distancia típica entre filas (la tira de precios bajo los
      productos), que aportan las repisas vacías. Cada nivel se mide solo
      donde su línea central queda dentro de la ROI (la repisa puede
      salir de la foto) y se descartan los niveles vacíos de menos de la
      mitad del alto típico (bordes de repisa). Vistas en ángulo
      sintéticas: `src/datasets/synthetic.py` (`oblique_view()`: giro de
      cámara como homografía K R K^-1, anotaciones transformadas,
      recortada sin bordes negros); solo con fotos que se pueden
      modificar (Kaggle CC0): la licencia de SKU-110K prohíbe obras
      derivadas. `scripts/evaluate_availability.py` ahora acepta
      `--dataset kaggle`, `--yaw`/`--pitch` y compara la variante
      `hibrido` con `segmentacion` (anotaciones como detector, ver #6).
      Resultados, alerta con libre >= 30% (híbrido / segmentación):
      SKU-110K `val` de frente (300 fotos usadas para ajustar / 288 de
      control), recall 0.9: falsas alertas con la góndola llena 6% / 4%
      y 6% / 3%; quiebre de 30% en el interior detectado 93% / 87% y
      94% / 88%. Kaggle (45 fotos), recall 0.9: de frente, falsas
      alertas 4% / 2% y quiebre de 30% 71% / 53%; girada 20° y 15° hacia
      abajo, 2% / 2% y 69% / 67%; girada 35° y 15° hacia abajo, 2% / 7%
      y 38% / 33% (quiebre de 40%: 91% / 93%). En resumen: de frente
      detecta más quiebres con algo más de falsas alertas (sus niveles
      no esconden huecos); con ángulo, la alerta global queda pareja,
      pero los niveles siguen las repisas, así que el detalle por repisa
      (Nivel 1) deja de mezclarlas. Foto real en ángulo (Kaggle 039, con
      `yolo26s` entrenado): 3 franjas que siguen las repisas, 5% libre y
      sin alerta (con la segmentación sola: 5 niveles cruzados, huecos
      falsos de 77% y 36%). Tests: 28 nuevos (18 en
      `tests/test_shelf_levels.py`, 6 en `tests/test_synthetic_views.py`
      y 4 nuevos en `tests/test_availability.py`). Limitaciones: el
      espacio libre se mide en píxeles de la imagen, y con perspectiva
      el tramo lejano de la repisa pesa menos que el cercano (corregirlo
      pide enderezar la góndola, la opción 3 que quedó pendiente); una
      última repisa con menos de 3 productos y sin borde visible no se
      mide; parámetros ajustados con las mismas fotos de SKU-110K y
      Kaggle (las 288 de control confirman SKU-110K de frente, pero no
      hay control con ángulo). Pendiente: usar `shelf_levels()` en
      `scripts/run_pipeline.py` (#8) y medir con el detector entrenado y
      fotos reales en ángulo.
- [x] **#21** (dueño: Francisco) Ajustar la documentación a que Walmart
      Chile no puede compartir imágenes reales de sus cámaras de
      seguridad, por privacidad (informado 2026-10-01). README
      ("Estrategia de Datos y Evaluación"), `docs/datasets.md` y los
      ítems #3, #4 y #14: la validación en condiciones de cámara de sala
      se hace con imágenes sintéticas tipo CCTV generadas desde datasets
      públicos (#14, paso 3), y la prueba ciega con el Dataset Oculto
      solo es posible si Walmart corre el sistema en sus instalaciones
      y entrega las métricas. Por confirmar con Walmart: si aceptan esa
      modalidad, y qué datos sin imágenes pueden entregar (modelo de
      cámara y lente, campo de visión, altura y ángulo de montaje,
      resolución y compresión de los fotogramas).
- [x] **#20** (dueño: Francisco) Dejar el repositorio listo para clonar
      e inicializar en un PC nuevo (Nicko, 2026-10-01). README: versión de
      Python, graphify con `uv tool` fuera del venv (instalado en el venv,
      los hooks de Claude Code no lo encuentran), `.env.example` para
      `ROBOFLOW_API_KEY`, activar el venv en PowerShell, `Integrante:
      <nombre>` en `CLAUDE.local.md`, PyTorch con CUDA solo para entrenar,
      y que `run_pipeline.py` aún no corre (#8). `CLAUDE.md`: cada sesión
      se orienta por `PROGRESS.md` (ítem en curso de la persona o el
      siguiente sin dueño; nada fuera del backlog). `docs/training.md` ya
      no manda a la rama del PR #15 (mergeada). Verificado con un clon
      limpio, venv nuevo en Python 3.14 y `pip install -r
      requirements.txt` (torch 2.14.1 CPU, ultralytics 8.4.171, pandas
      3.0.6): imports de todas las librerías y de `src/`, `--help` de los
      7 scripts, `graphify update .` y `pytest tests/` 137 OK. En un PR
      aparte, `tests/test_models.py` deja de fallar en PCs con GPU NVIDIA
      (`.cpu().numpy()`).
- [x] **#23** (dueño: Francisco) Fechas de entregas y plazos en
      `README.md` y `PROGRESS.md`, en formato YYYY-MM-DD en la línea de
      la tarea: Evaluación 2 (Avance) de la Fase 2 y cierre del Sprint 1
      la semana del 2026-10-28, Fase 3 por definir, y decidir la versión
      de Python de la imagen a más tardar 2026-10-16.
- [x] **#25** (dueño: Francisco) Registro de requisitos y plazos del
      curso en `docs/curso.md` (próximos hitos, requisitos vigentes,
      anuncios pendientes, preguntas abiertas y registro por semana),
      con la skill `/mensaje-profesor` que normaliza cada mensaje del
      profesor. Flujo en `CLAUDE.md` ("Mensajes del profesor"). Primer
      mensaje registrado: semana 8 (Evaluación 2 y documentos de la Fase
      2). Los enlaces no se versionan (repositorio público): se anota la
      fecha del mensaje que los trae.
- [x] **#8** (dueño: Francisco) `scripts/run_pipeline.py`: pipeline
      completo sobre fotos o carpetas. `src/pipeline.py` (`run_image()`)
      encadena `correct_image()` -> `segment_gondola()` -> `crop_roi()` ->
      detector -> `shelf_levels()` -> `compute_availability()` y lleva el
      resultado a la foto original (polígonos densificados: con lente,
      repisas y huecos se ven curvos). `src/reporting/annotate.py`
      dibuja la vista limpia (huecos en rojo, % libre por repisa, cartel
      de alerta). Por foto: `<nombre>.jpg` y `<nombre>.json`, más una
      tabla de segundos por etapa. Incluye la evaluación por lotes de
      CU07 (RF06): `--annotations` (CSV estándar) compara por IoU
      (`src/evaluation/detection_metrics.py`) y la alerta con la de la
      anotación (`measure_boxes()`), y escribe `metrics.csv`. Tests: 28
      nuevos (góndola sintética y detector falso por color en
      `tests/pipeline_fixtures.py`); INT-02 e INT-03 pasan. RF01 en CPU:
      mediana 0.70 s por foto (6 fotos de Kaggle). Diseño en
      `docs/superpowers/specs/2026-10-07-run-pipeline-design.md`.
- [x] **#30** (dueño: Francisco) Documentación alineada con las
      reuniones con Walmart (2026-09-03, 2026-09-16 y 2026-09-30). Las
      minutas no se versionan (son confidenciales y el repositorio es
      público): el README resume los acuerdos sin transcribirlos.
      README: supuestos de fachada visible, sin apilamiento, una sola
      clase y qué se mide (sin bodega superior ni islas); profundidad de
      25 cm a la espera de las medidas estándar; tabla "Acuerdos con el
      Cliente" con fecha y estado (el sentido del umbral y el alcance
      quedan por confirmar, #24); RF01 acepta lotes de fotos; RF04 alerta
      por góndola; RF05 con contenido mínimo; RF06 nuevo (evaluación por
      lotes); evaluación de Walmart por IoU y fotos propias (#32).
      Casos de uso (`Anexos/Diseño/Plantilla de C.U 0X.docx`): CU01 con
      el pipeline real (YOLO26, segmentación, sin bodega ni islas,
      excepciones de góndola no encontrada y cámara defectuosa) y sin
      exigir 1 cámara = 1 góndola; CU02 y CU03 con el umbral expresado
      como espacio libre configurable, canal de alerta definido,
      confirmación de la reposición con la captura siguiente y
      postcondición propia; CU03 sin "tiempo real"; CU04 sin
      "categoría" (el detector tiene una sola clase), con el actor del
      diagrama y una excepción; CU05 con calibración de lente y
      profundidad fija; CU06 sin enviar contraseñas por correo; CU07
      nuevo: evaluar el sistema con un lote de imágenes (cubre el
      Dataset Oculto). Los textos se editaron sin cambiar el formato y
      los 8 archivos se verificaron abriéndolos en Word. Diagramas
      regenerados (CU00 sin cambios): el general, con CU07, CU02
      `<<extend>>` de CU01 y CU07 `<<include>>` de CU01, y los de
      secuencia de CU01 a CU07, alineados con las plantillas (CU05 ya no
      dibuja ROI). Sus fuentes quedan en `Anexos/Diseño/Diagramas fuente
      (Mermaid)/` (`.drawio` del general y `.mmd` de cada C.U, con
      `LEEME.md`); `.gitignore` deja versionar los PNG de `Anexos/`.
      `docs/curso.md` lista los 8 C.U. Ítems
      nuevos: #31 (bodega superior), #32 (fotos propias y set anotado)
      y #33 (verificar el detector fuera de SKU-110K). Se numeraron
      primero #26-#29 y se renumeraron (#30-#33) porque el PR de la semana
      8 usó esos números al mismo tiempo.
- [x] **#40** (dueño: Francisco) Quiebre de stock por góndola completa
      (cambio de alcance del profesor, 2026-10-19). La alerta y el %
      libre que se informan son solo los de la góndola completa; la
      medición no cambia (`shelf_levels()` y la cobertura a lo largo de
      cada repisa). Código: `ShelfAvailability` sin `critical` (su %
      libre queda como dato interno de medición) y sin
      `GondolaAvailability.critical_shelves`; `ShelfResult` y su JSON
      solo con geometría (`level_index`, `polygon`, `gaps`,
      `product_count`); la vista mantiene los huecos en rojo, el
      contorno de cada repisa y el cartel de la góndola, sin la etiqueta
      "Repisa N - x% libre". Tests primero (TDD): una repisa sobre el
      umbral no alerta si la góndola no lo alcanza, el JSON por repisa
      no trae % ni alerta y la vista no tiene etiquetas por repisa;
      `pytest` 195 passed. Pipeline real en CPU (`yolo26s`) sobre 3
      fotos de Kaggle (003, 017, 031): 003 da una falsa alerta (41%
      libre; refrigerador con la fila de abajo llena marcada como
      hueco), hallazgo para #34/#33. Casos de uso CU01 a CU04 (solo el
      texto de los `<w:t>`, verificados en Word) y diagramas de CU01,
      CU02, CU03, CU04 y CU07 (fuentes `.mmd` y PNG regenerados con
      mermaid-cli, tema oscuro; configuración en
      `mermaid-config.json`). README ("Ejecución local") y
      `docs/test-plan.md` (AV-01, RF04 y registro). Sigue pendiente,
      en otros ítems: ítem #35 (justificar que las repisas son método de
      medición, no salida) y las preguntas abiertas de `docs/curso.md`
      (si una foto con varias góndolas o módulos da una o varias
      alertas; si sigue el umbral de 30%).
- [x] **#41** (dueño: Francisco) Plugin `ponytail` para el trabajo con
      código (pedido de Francisco, 2026-10-19): skill `/ponytail` de
      github.com/DietrichGebert/ponytail (MIT), compartida en
      `.claude/settings.json` y fija en v5.3.2. Revisados sus *hooks*
      antes de instalar: corren Node en local (reglas y mapa del repo al
      iniciar la sesión); el registro de costos (`ledger`) queda
      desactivado y el *webhook* vacío. Regla de uso en `CLAUDE.md`
      ("Reglas de código" y regla 9) y paso de instalación en el README.

- [x] **#26** (dueño: Mariana) Plan de mejoras de la Fase 1, en
      `docs/plan-de-mejoras.md` (2026-10-20; el plazo era 2026-10-09).
      La Fase 1 tuvo nota 7,0 sin observaciones escritas, así que el
      plan contrasta lo comprometido en la guía 1.5 y los anexos con el
      proyecto actual y con la pauta de avance de la Fase 2. Define 10
      mejoras (M1 a M10) con acciones, responsables, fechas, evidencia
      y estado: objetivos medibles, metodología ajustada, riesgos
      reales, evidencias, monitoreo del plan, diseño alineado con la app
      Django, competencias, inglés, aporte visible de cada integrante y
      validación fuera de SKU-110K. Varias ya están en curso; los
      responsables de las que no tienen ítem con dueño son propuestos,
      a confirmar por el equipo. El seguimiento se hace en la columna
      "Estado" del documento.

## Notas

- Cambio de alcance (2026-09-27): la ROI de la góndola la segmenta el
  sistema automáticamente (antes el Administrador la definía a mano) y la
  profundidad de góndola es constante, de 20-30 cm. Ya están actualizados
  README, CLAUDE.md, `docs/datasets.md` y `roi_filter.py`. Siguen
  desactualizados estos anexos de diseño, que no se modificaron:
  `Anexos/Diseño/Mockups/Mockup Admin-1.jpg` (pantalla "Editor de Región
  de Interés (ROI)" con el botón "Guardar Máscara ROI"),
  y `Mockup Admin-4.jpg` (log "Actualizó máscara ROI"). Actualizarlos
  quedó postergado para más adelante (decidido 2026-09-27). Las
  plantillas de C.U ya están al día (#30).
- Riesgos de Docker resueltos y verificados con `docker build` real
  (2026-09-27, Docker Desktop 4.92): imagen de 2.49 GB, 27/27 tests OK
  dentro del contenedor. El build real destapó un cuarto problema: el pip
  23.0.1 de la imagen base rechazaba wheels del índice de PyTorch, así que
  el Dockerfile ahora actualiza pip antes de instalar. Detalle de los
  otros tres:
  - OpenCV: se usa solo `opencv-python>=4.8,<5` (ultralytics lo exige; el
    `-headless` duplicaba `cv2`). Tope `<5` porque pip ya resolvía
    OpenCV 5.0 sin validar.
  - Base fijada a `python:3.10-slim-trixie` (Debian 13): `libgl1-mesa-glx`
    y `libglib2.0-0` no existen ahí. Paquetes de sistema derivados de las
    dependencias ELF reales del wheel de OpenCV 4.14 (`readelf` en WSL) y
    verificados en el archivo de Debian trixie.
  - PyTorch CPU desde `download.pytorch.org/whl/cpu`: desde PyPI en Linux
    arrastraba CUDA 13 + cuDNN (varios GB). Resolución final verificada
    con `uv pip compile` para Linux/py3.10: `torch 2.14.0+cpu`,
    `ultralytics 8.4.164`, `opencv-python 4.14.0.94`, sin paquetes CUDA.
- Python de la imagen y del CI: 3.13 (decidido 2026-10-18, #28). 3.10
  termina su soporte en octubre de 2026 y Django 6.1 exige 3.12 o
  superior; la suite ya corría en 3.14 en local.
- La carpeta `Fase 1/` (entregables de la Fase 1 académica) no se toca.
- README.md se actualizará incrementalmente a medida que se implementen
  los módulos.
- Los 2 datasets de Roboflow se descargaron manualmente (export ZIP en
  formato COCO). `scripts/download_datasets.py` los descarga si cada
  integrante configura su API key personal de Roboflow en
  `ROBOFLOW_API_KEY` o `.env`; sin key, se pueden copiar desde otro
  integrante (CC BY 4.0) y validar con `--check`.
