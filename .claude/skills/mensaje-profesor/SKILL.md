---
name: mensaje-profesor
description: "Registra un mensaje del profesor del curso (APT122) en docs/curso.md, normalizado: hitos con fecha YYYY-MM-DD, requisitos, pendientes y preguntas abiertas, y lleva las fechas a README.md y PROGRESS.md. Usar cuando la persona pega un mensaje o correo del profesor, o dice 'mensaje del profesor', 'nuevo mensaje del profe' o /mensaje-profesor."
argument-hint: "Fecha del mensaje (YYYY-MM-DD o semana N) y el texto del mensaje"
user-invocable: true
---

# Registrar un mensaje del profesor

La persona pega un mensaje del profesor junto con la fecha en que llegó.
Tu trabajo es dejar `docs/curso.md` al día, en formato normalizado, y
llevar sus fechas a los archivos de estado. No se copia el mensaje
textual.

## 1. Preparar

1. Si la fecha del mensaje no viene, preguntarla (sirve "semana N").
   Para traducir semanas a fechas, usar el registro de `docs/curso.md`
   (ej. "Semana 8 (2026-10-05 a 2026-10-09)"); si la semana no aparece
   ahí, preguntar sus fechas.
2. Rama: respetar "Trabajo en equipo" de `CLAUDE.md`. Si ya se está en
   una rama de trabajo propia, seguir ahí; si no, desde `main`
   actualizado crear `docs/curso-<YYYY-MM-DD>` (fecha del mensaje).
   Registrar mensajes del profesor no necesita ítem en `PROGRESS.md`.
3. Leer `docs/curso.md`, la sección "Planificación y Cronograma" de
   `README.md` y "Pendientes (priorizados)" de `PROGRESS.md`.

## 2. Extraer del mensaje

- **Hitos**: evaluaciones, entregas, presentaciones, reuniones. Para
  cada uno: fecha, nombre, qué se entrega y con qué criterio.
- **Requisitos**: lo que se pide o cómo se evalúa (ej. "50% de los C.U
  resueltos").
- **Anuncios pendientes**: lo que el profesor dice que enviará después.
- **Material**: documentos, plantillas, imágenes o enlaces compartidos.
- **Cambios**: si contradice o reemplaza algo ya registrado.

## 3. Reglas de normalización

- Fechas siempre en YYYY-MM-DD, en la misma línea del hito o tarea. Las
  relativas se resuelven con la fecha del mensaje ("el próximo lunes"
  -> fecha exacta); "la semana del 28/octubre" -> "Semana del
  2026-10-28". El año es el del mensaje salvo que diga otro.
- **Nunca inventar fechas**: si no se puede deducir con certeza,
  escribir "Por definir" o "(día exacto por confirmar)" y agregar la
  duda a "Preguntas abiertas para el profesor".
- **Enlaces fuera del repositorio** (es público): no escribir URLs de
  Drive, formularios ni similares en archivos versionados. Escribir
  "en Drive (enlace en el mensaje del profesor del <YYYY-MM-DD>)", con
  la fecha del mensaje (o "de la semana N" si no hay día exacto), para
  que el equipo encuentre el mensaje que trae el enlace. Guardar el
  enlace, con esa misma fecha, en la sección "Enlaces del curso
  (privados)" de `CLAUDE.local.md` (crearla si no existe).
- Sin datos personales de terceros (correos, teléfonos). Al profesor se
  le nombra "el profesor".
- Si el mensaje menciona una imagen o adjunto que no llegó, pedirlo; si
  llega, registrar su contenido como texto en "Requisitos vigentes".
- Español, frases cortas, sin copiar el tono del mensaje.

## 4. Actualizar `docs/curso.md`

- **Registro de mensajes**: nueva subsección arriba de las anteriores,
  `### Semana N (YYYY-MM-DD)` o con el rango de la semana, con un punto
  por idea del mensaje.
- **Próximos hitos**: agregar o actualizar filas, ordenadas por fecha
  ("Por definir" al final), con la semana del mensaje como fuente. Si
  un hito cambia, actualizar la fila y anotar en el registro
  "cambia <hito>: antes <fecha>, ahora <fecha>". Los hitos ya pasados
  se quitan de la tabla (quedan en el registro).
- **Requisitos vigentes**, **Pendiente de parte del profesor** y
  **Preguntas abiertas**: agregar lo nuevo y quitar lo que el mensaje
  resuelve.

## 5. Llevar a los archivos de estado

- `README.md` ("Planificación y Cronograma"): si el hito es de una fase
  (evaluación, entrega, pre-examen, exposición), escribir su fecha en
  la línea de esa fase. No cambiar los rangos de semanas salvo que el
  mensaje los cambie explícitamente.
- `PROGRESS.md`: si cambia el cierre del Sprint (línea bajo el título),
  actualizarla. Si un requisito implica trabajo que no está en el
  backlog, **proponer** el ítem a la persona; agregarlo solo si
  confirma (con su dueño, regla "Nada fuera del backlog").

## 6. Cerrar

- Mostrar a la persona: qué se registró, qué fechas se movieron, el
  riesgo para el próximo hito si lo hay (comparando el requisito con el
  estado de `PROGRESS.md`) y las preguntas abiertas.
- No hacer commit ni push salvo que la persona lo pida (regla 4 de
  `CLAUDE.md`). Si lo pide: `docs: record course message of
  <YYYY-MM-DD>` y PR contra `main`.
