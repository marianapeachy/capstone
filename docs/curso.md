# Curso APT122: requisitos y plazos

Lo que va pidiendo el profesor, normalizado: fechas en formato
YYYY-MM-DD, requisitos concretos y lo que queda por aclarar. Se
actualiza con la skill `/mensaje-profesor` (ver "Mensajes del profesor"
en `CLAUDE.md`); no se copian los mensajes textuales.

Los enlaces que comparte el profesor (Drive, formularios) no se anotan
aquí porque el repositorio es público. Cada mención dice la fecha (o
semana) del mensaje que trae el enlace, para buscarlo ahí.

## Próximos hitos

| Fecha | Hito | Qué se entrega / criterio | Fuente |
| --- | --- | --- | --- |
| Ya esperado (sin fecha) | CRUD principales y Login operativos | Según los perfiles de usuario (Reponedor, Jefe de Salón, Administrador) | Semana 8 |
| 2026-10-21 | Informe intermedio de avance y video de demostración | Informe con los puntos pedidos por el cliente (ver "Requisitos vigentes") y video de 5 a 10 minutos; todo disponible en el repositorio GitHub. Evalúa el avance real, no el producto final | Semana 9 |
| Semana del 2026-10-26 (día y hora por informar) | Feria de informática | Se presenta al menos 1 integrante por equipo | Semana 9 |
| A más tardar 2026-10-26 | Evidencias de avance de la Fase 2 | Documentos administrativos de AVANCE (Drive, ver "Requisitos vigentes") y GitHub con el README bien documentado | Semana 9 |
| Semana del 2026-10-28 (día exacto por confirmar) | Evaluación 2 (Avance), Fase 2 | 50% de los C.U de la fase resueltos; se muestra la demo del Sprint 1 | Semana 8 |
| A más tardar 2026-10-31 | Primer demo operativo | Demo funcional para mostrar avances concretos al cliente (Walmart) y recibir su evaluación y retroalimentación | Semana 8 |
| Semana 15 (por confirmar: 2026-11-23 a 2026-11-27 si no hay semanas de receso) | Entrega final Fase 2 | Documentos de la Fase 2 (ver "Requisitos vigentes") en la carpeta "FINAL FASE 2" de Drive (detalles por anunciar) | Semanas 8 y 9 |
| Por definir | Instalación en el servidor del CITT | La aplicación queda instalada en el servidor del CITT; instrucciones por sección por llegar | Semana 9 |
| Por definir | Pre-examen (Fase 2) | - | README |
| Por definir | Exposición ante la Comisión (Fase 3) | - | README |

## Requisitos vigentes

- **Evaluación 2 (Avance)**: el 50% de los casos de uso de la fase
  resueltos. Los C.U del diseño son 8 (CU00-CU07, en
  `Anexos/Diseño/Plantilla de C.U 0X.docx`): CU00 autenticar usuario,
  CU01 ingestar y analizar imagen, CU02 notificar alerta de quiebre,
  CU03 dashboard de disponibilidad, CU04 exportar reporte, CU05
  configurar cámara y umbrales, CU06 gestionar cuentas y roles, y CU07
  evaluar el sistema con un lote de imágenes (agregado en #30).
- **CRUD y Login**: a esta altura el profesor espera los CRUD
  principales y el Login operativos, según los perfiles de usuario
  (Reponedor, Jefe de Salón, Administrador). Corresponde a CU00 y CU06
  (y CU05 si la configuración de cámaras y umbrales cuenta como CRUD
  principal). Implica base de datos, que también piden las evidencias
  del sistema.
- **Primer demo operativo** a fines de octubre (a más tardar
  2026-10-31): funcional y mostrable al cliente, para recibir su
  evaluación y retroalimentación.
- **Plan de mejoras**: se elabora y empieza a implementar en la semana
  8, a partir de las observaciones de la evaluación y rúbrica de la
  Fase 1.
- **Informe intermedio de avance** (entrega 2026-10-21; lo pide el
  cliente, Walmart). No evalúa el producto final sino el avance real,
  las dificultades técnicas y las mejoras para las próximas entregas.
  Los resultados deben ser realistas y con evidencias: analizar bien
  los errores vale tanto como mostrar los aciertos. Puntos mínimos:
  1. **Estado de avance**: actividades realizadas y módulos operativos;
     estado de cada módulo (terminado, en desarrollo o pendiente) con
     porcentaje estimado respaldado por evidencias; Carta Gantt
     actualizada (hitos cumplidos, retrasos, pendientes); dificultades
     y riesgos técnicos (causas y acciones); próximos pasos con
     responsable y fecha.
  2. **README.md** del repositorio al día: descripción de la solución
     (problema, objetivos, funcionalidades), estrategia técnica
     (tecnologías, librerías, algoritmos, modelos), justificación
     técnica de cada elección (no basta enumerarlas), arquitectura con
     diagramas de componentes, módulos y flujos, datasets (origen,
     cantidad de imágenes, limpieza, etiquetado y preparación) y estado
     de la implementación (operativo y pendiente).
  3. **Análisis de resultados preliminares** (el punto más importante):
     - 10 mejores casos: imagen de entrada, resultado de la aplicación,
       resultado esperado, por qué es exitoso y métrica o criterio.
     - 10 peores casos: imagen de entrada, resultado, error detectado,
       posibles causas y propuesta de mejora. Considerar iluminación,
       perspectiva, sombras, reflejos, oclusiones, calidad de imagen y
       errores de detección o segmentación.
     - Análisis comparativo de los 20 casos: condiciones en que funciona
       bien, patrones de error, limitaciones, mejoras posibles y
       acciones prioritarias, con métricas cuantitativas cuando
       corresponda (% de aciertos, precisión, errores de detección,
       tiempos de procesamiento).
     - Licencia: las imágenes de SKU-110K no se pueden mostrar a
       terceros (ver `CLAUDE.md`); los casos del informe salen de
       datasets que lo permiten (Kaggle CC0, SHARD, Roboflow) o de
       fotos propias.
  4. **Repositorio y reproducibilidad**: estructura de carpetas y
     código, README completo, instrucciones de instalación,
     configuración y ejecución, diagramas, documentación técnica y
     evidencias, historial de commits que muestre el avance y la
     participación de cada integrante, y ejemplos para comprobar que
     funciona. Una persona externa debe poder entender y reproducir la
     ejecución con la documentación.
  5. **Conclusiones y plan de mejora**: objetivos alcanzados,
     funcionalidades realmente operativas, dificultades pendientes,
     mejoras a priorizar, lo que falta para el MVP y si el alcance es
     viable en el tiempo disponible; plan de mejora con actividades,
     responsables y fechas.
  6. **Demostración funcional** (en el mensaje es el punto 7): video de
     5 a 10 minutos, solo con funcionalidades implementadas y
     resultados que la aplicación genera hoy.

  Toda la documentación y las evidencias quedan organizadas en el
  repositorio GitHub.
- **Feria de informática** (semana del 2026-10-26): compromiso de que
  se presente al menos 1 integrante por equipo.
- **Servidor del CITT**: la aplicación también debe quedar instalada en
  el servidor del CITT (pedido desde el inicio del semestre). El
  director de carrera lo coordina entre las secciones de Capstone.
- **Impedimentos**: toda dificultad que pueda afectar estos avances se
  informa al profesor a tiempo.
- **Alcance del quiebre de stock** (cambio del 2026-10-19): el quiebre
  se determina sobre la **góndola completa**, no por nivel o repisa. La
  alerta y el porcentaje de espacio libre que entrega el sistema son los
  de la góndola completa; las repisas quedan solo como método interno
  para medir (con cámara en ángulo miden mejor, ítem #22). Reemplaza el
  "análisis segmentado por repisa" del Nivel 1 (acta de la primera
  reunión con Walmart). Trabajo en el ítem #40 de `PROGRESS.md`.
- **SKU-110K**: se puede trabajar con él (entrenar y evaluar), confirmado
  el 2026-10-19. Siguen las restricciones de su licencia (de Trax, el
  dueño del dataset): sus fotos no se muestran a terceros ni se usan
  para generar imágenes derivadas (ver `CLAUDE.md`).
- **Documentos de la Fase 2**: las plantillas están en Drive (enlace en
  el mensaje del profesor de la semana 8, 2026-10-05 a 2026-10-09). El
  profesor volvió a compartir los de AVANCE, pedidos por auditoría, en
  otra carpeta de Drive (enlace en el mensaje del profesor del
  2026-10-16): fecha tope de las evidencias de avance 2026-10-26; la
  Fase 2 final es en la semana 15.
  - Evidencias individuales (cada integrante):
    `Apellido_Nombre_2.1_APT122_DiarioReflexionFase2.docx`.
  - Evidencias grupales: `2.4_GuiaEstudiante_Fase 2_DesarrolloProyecto
    APT.docx`, `PLANILLA DE EVALUACIÓN AVANCE FASE 2.xlsx`,
    `2.6_GuiaEstudiante_Fase 2_Informe Final Proyecto APT.docx` y
    `PLANILLA DE EVALUACIÓN FINAL FASE 2.xlsx`. Las dos guías van en
    español; su versión en inglés es optativa.
  - Evidencias del proyecto: presentación del proyecto, evidencias de
    documentación y evidencias del sistema (aplicación y base de
    datos).
  - Carpeta de AVANCE (revisada el 2026-10-17; archivos del
    2026-10-16): 2.1 diario de reflexión, 2.2 autoevaluación del
    avance, 2.3 formativa del avance, 2.4 guía de desarrollo del
    proyecto, 2.6 guía del informe final y las planillas de evaluación
    de avance y final. Las 2.2 y 2.3 no estaban en la lista de la
    semana 8.
- **Documentos de AVANCE, contenido** (de la carpeta del 2026-10-16):
  - **2.1 Diario de reflexión** (se responde en grupo y se sube a la
    sección de reflexión de la Fase 2): cumplimiento de la Carta Gantt
    y factores que lo facilitaron o dificultaron; cómo se enfrentan las
    dificultades; autoevaluación del trabajo; dudas para el docente o
    los pares; si hay que redistribuir actividades; evaluación del
    trabajo en grupo.
  - **2.2 Autoevaluación del avance** (individual, formativa, 0%;
    semana 9 en el taller) y **2.3 Formativa del avance** (grupal,
    formativa, 0%; semana 7): misma pauta del informe de avance.
    Indicadores: ajustes al proyecto justificados por dificultades,
    facilitadores y retroalimentación; metodología que logra los
    objetivos; evidencias de avance; lenguaje técnico; redacción,
    ortografía y citas; formato; indicadores de calidad del perfil de
    egreso (pruebas de validación, gestión de proyecto, modelos de
    datos, construcción, integración e implantación del software); y
    redacción en inglés nivel intermedio alto.
  - **Formato del informe de avance** (según 2.2 y 2.3): informe
    técnico con portada, índice, abstract (inglés y español),
    desarrollo de ingeniería, conclusiones y reflexiones individuales
    (estas dos, solo en inglés); Arial, Verdana o Calibri 11 o 12;
    interlineado 1,0 o 1,5; número de página; bibliografía y anexo de
    evidencias si corresponde.
  - **2.4 Guía de desarrollo del proyecto**: (1) resumen del avance
    (actividades, objetivos específicos cumplidos y cómo; objetivos y
    metodología solo si se ajustaron; evidencias de avance y cómo se
    resguardó la calidad, adjuntándolas); (2) monitoreo del plan de
    trabajo: tabla con competencia, actividad, recursos, duración,
    responsable, observaciones, estado (En curso, Con retraso, No
    iniciado, Completado, Ajustada) y ajustes; (3) ajustes a partir del
    monitoreo: facilitadores y obstáculos, actividades ajustadas o
    eliminadas y actividades atrasadas o no iniciadas, con su
    estrategia.
  - **Planilla de evaluación del avance** (grupal, nota de 1,0 a 7,0):
    ajustes justificados (10), metodología (10), evidencias de
    documentación, programación y almacenamiento de datos según lo
    planificado y con estándares de la industria (25), lenguaje
    técnico (5), redacción y citas (5), documentación con la
    estructura y nombres pedidos y todas las evidencias de avance en
    Git (20), aporte de cada integrante visible en el repositorio, con
    participación equitativa (15), y trabajo en equipo: todos dominan
    el tema al exponer (10).
- **Fase 1** (ya entregada, como referencia): individuales 1.1
  autoevaluación de competencias, 1.2 diario de reflexión y 1.3
  autoevaluación; grupales presentación de la idea, 1.4 formativa, 1.5
  guía de definición del proyecto (inglés optativo) y planilla de
  evaluación (enviada por correo).

## Pendiente de parte del profesor

- Detalles de la carpeta "FINAL FASE 2" en Drive (anunciado en la
  semana 8).
- Día y hora de la feria de informática (semana del 2026-10-26;
  anunciado el 2026-10-16).
- Instrucciones por sección para instalar la aplicación en el servidor
  del CITT (anunciado el 2026-10-16).

## Preguntas abiertas para el profesor

- ¿Qué cuenta como "C.U resuelto" para la Evaluación 2? Ya se sabe que
  espera Login y CRUD (CU00, CU06): ¿qué otros CRUD cuentan como
  "principales" (cámaras, góndolas, umbrales: CU05)?
- ¿El primer demo operativo (fines de octubre) se presenta a Walmart en
  una reunión aparte o dentro de la Evaluación 2?
- ¿Qué día de la semana del 2026-10-28 es la Evaluación 2, y es
  presentación, entrega de documentos o ambas?
- ¿Qué documentos de la Fase 2 van en la Evaluación 2 (Avance) y cuáles
  en la entrega final? Por sus nombres, la guía 2.4 y la planilla de
  avance serían del Avance, y la guía 2.6 y la planilla final, de la
  entrega final. El mensaje del 2026-10-16 dice que lo que adjunta
  "solo corresponde AVANCE", pero la carpeta trae también la guía 2.6
  y la planilla final: ¿cuáles se entregan a más tardar el 2026-10-26?
- ¿Qué fechas tiene la semana 15 (entrega final de la Fase 2)? Contando
  desde la semana 8 (2026-10-05) sería 2026-11-23 a 2026-11-27, si no
  hay semanas de receso.
- El informe intermedio (2026-10-21), ¿es el mismo informe de estado de
  avance que pidió el correo de la semana 7? Las pautas 2.2 y 2.3 dan
  el formato del informe de avance (ver "Requisitos vigentes"): ¿el
  informe intermedio sigue ese formato o es otro documento? ¿Por qué
  medio se entrega (repositorio, PDF, Drive) y dónde se sube el video?
- El mensaje numera los puntos del informe del 1 al 5 y luego el 7:
  ¿falta un punto 6?
- ¿Qué componentes debe tener la instalación en el servidor del CITT
  (aplicación web, base de datos, modelo YOLO26)? ¿El servidor tiene
  GPU y Docker?
- Quiebre por góndola completa (2026-10-19): ¿una foto equivale a una
  góndola? Si la foto muestra varias góndolas o módulos (de ~1 m), o un
  pasillo entero, ¿se da una alerta por foto o por cada góndola? ¿El
  cambio viene del cliente (Walmart)? ¿Sigue valiendo el umbral de 30%
  de espacio libre del frente de la góndola?
- SKU-110K (2026-10-19): "trabajar sin problemas", ¿incluye mostrar sus
  fotos en el informe intermedio, el video o la demo ante Walmart? Su
  licencia lo prohíbe; mientras no haya un permiso de Trax, esos casos
  salen de Kaggle CC0, SHARD o Roboflow.

## Registro de mensajes

Del más reciente al más antiguo.

### Semana 10 (2026-10-19): alcance por góndola completa y SKU-110K

Mensaje contado por un integrante (sin texto literal).

- Cambio de alcance: el quiebre de stock se determina sobre la góndola
  completa, no por nivel o repisa. Cambia el Nivel 1: antes, % libre y
  alerta por repisa; ahora, solo de la góndola completa (detalle en
  "Requisitos vigentes"; trabajo en el ítem #40).
- Se puede trabajar con SKU-110K sin problemas. Se registra como
  confirmación para entrenar y evaluar; su licencia sigue impidiendo
  mostrar sus fotos a terceros (pregunta abierta).

### Semana 9 (2026-10-16): informe intermedio, feria y servidor CITT

- Reenvió el correo del cliente (Walmart) que pide un informe
  intermedio de avance del proyecto: estado de avance, README,
  análisis de 10 mejores y 10 peores casos, repositorio reproducible,
  conclusiones con plan de mejora y video de demostración de 5 a 10
  minutos (detalle en "Requisitos vigentes").
- Entrega del informe y el video: 2026-10-21 (miércoles), porque el
  cliente posiblemente no visite el viernes de esa semana
  (2026-10-23).
- Cambia el informe de estado de avance (semana 8): antes "ya
  esperado", sin fecha; ahora es el informe intermedio, 2026-10-21.
- Feria de informática la semana del 2026-10-26: al menos 1 integrante
  por equipo; día y hora por informar.
- La aplicación debe quedar instalada en el servidor del CITT; el
  director de carrera lo coordina y las instrucciones por sección
  llegan en los próximos días.
- Volvió a compartir en Drive los documentos administrativos de la
  Fase 2 que pide auditoría, solo los de AVANCE (enlace en este
  mensaje). Pide el README del GitHub bien documentado. Contenido de la
  carpeta en "Requisitos vigentes" (revisada el 2026-10-17).
- Fecha tope de las evidencias de avance de la Fase 2: 2026-10-26
  (lunes). La entrega final de la Fase 2 es en la semana 15.

### Semana 8 (2026-10-05 a 2026-10-09): actividades de la semana

- Plan de mejoras: elaborarlo y empezar a implementarlo esta semana,
  según las observaciones de la evaluación y rúbrica de la Fase 1.
- Los equipos ya deberían tener los CRUD principales y el Login
  operativos, según los perfiles de usuario.
- Primer demo operativo a fines de octubre (a más tardar 2026-10-31),
  para mostrar avances concretos al cliente y recibir su evaluación.
- Espera el informe de estado de avance de cada equipo, con los puntos
  del correo que envió la semana 7.
- Pide revisar las observaciones pendientes, priorizar lo necesario
  para el demo e informar a tiempo cualquier impedimento.
- Responde la pregunta de si hace falta base de datos: sí, CRUD y Login
  la necesitan.

### Semana 8 (2026-10-05 a 2026-10-09): Evaluación 2 y documentos

- La semana del 2026-10-28 es la Evaluación 2 (Avance): se espera el
  50% de los C.U de la fase resueltos.
- Compartió en Drive los documentos administrativos de la Fase 2 (el
  enlace está en este mensaje), con una imagen que los lista (ver
  "Requisitos vigentes").
- Anunció que pronto enviará los detalles de la carpeta "FINAL FASE 2"
  de Drive.
