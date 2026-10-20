# Auditoría de la app web antes de publicarla (2026-10-18)

Revisión de la app web (`web/`, ítem #28) contra los requerimientos
(`Anexos/Diseño/Lista de Requerimientos.xlsx`: RF01-RF09, RNF01-RNF06),
los casos de uso CU00-CU07, los mockups de la Fase 1 y los acuerdos con
Walmart del README. Las minutas de las reuniones no estaban en el PC donde
se hizo la revisión: se usó el resumen público del README.

Estado al cerrar el PR de #28: los once P0 quedaron resueltos (ver
`PROGRESS.md`, #28); los P1 y P2 siguen en los ítems indicados.

Prioridad: **P0** se resuelve antes de subir el PR; **P1**, antes de la
Evaluación 2 y del demo con Walmart (semana del 2026-10-28, a más tardar
2026-10-31); **P2**, backlog de la Fase 2.

## Lo que necesita cada perfil

| Perfil | Dónde | Lo que necesita resolver en segundos | Hoy |
| --- | --- | --- | --- |
| Reponedor | Teléfono, en el pasillo, una mano ocupada | Qué góndola reponer primero, dónde está y avisar que la tomó o la terminó (CU02) | Ve una lista de análisis con quiebre, sin ubicación ni acciones |
| Jefe de Salón | PC de la tienda | Subir una foto, ver qué góndolas están en quiebre y quién las atiende (CU01, CU03) | Sube fotos y ve la lista y el detalle |
| Administrador | PC | Crear, editar y desactivar cuentas (CU06); umbral y cámaras (CU05) | CU06 completo; CU05 no existe |

## Hallazgos

| # | Hallazgo | Requisito | Prioridad | Decisión |
| --- | --- | --- | --- | --- |
| 1 | Una alerta no dice dónde está la góndola: el análisis solo guarda el nombre del archivo. Sin pasillo y góndola el reponedor no puede actuar, y CU03 y CU04 no pueden agrupar ni filtrar | CU02 paso 2, CU03, CU04, RF05 | P0 | Pasillo y góndola obligatorios al subir la foto |
| 2 | La alerta no tiene ciclo de vida: no se puede tomar ni completar, y dos fotos de la misma góndola generan dos alertas | CU02 pasos 5-6 y flujo 2a | P0 | Estados Activa, En proceso (quién y desde cuándo) y Completada; una foto nueva de la góndola reemplaza a la alerta abierta anterior |
| 3 | La interfaz no está pensada para el teléfono del reponedor (tabla ancha, botones chicos) | CU02 paso 3, RF05 "interfaz adaptativa" | P0 | Vista de alertas para teléfono, con objetivos táctiles grandes |
| 4 | El estilo depende de un CDN (Pico CSS): sin internet en la red de la tienda o en el servidor del CITT la app se ve sin estilos | RNF06, #39 | P0 | Estilos propios dentro de la app, sin depender de CDN |
| 5 | Faltan estados vacíos, de error y las páginas 403/404 con el estilo de la app | Craft, RNF06 | P0 | Agregar los estados y las páginas |
| 6 | La sesión no expira por inactividad | RNF04 | P0 | Expira tras 2 h sin uso (cubre un turno sin pedir login a cada rato) |
| 7 | No hay límite de tamaño para la foto subida | Seguridad | P0 | Máximo 20 MB, validado en el formulario |
| 8 | Un Administrador puede desactivarse a sí mismo y quedar fuera | CU06 | P0 | El formulario lo impide |
| 9 | No se valida el dígito verificador del RUT: un RUT mal escrito crea una cuenta con la que nadie puede entrar | CU00, CU06 | P0 | Validar el RUT al crear o editar |
| 10 | La primera foto tarda ~7 s porque el modelo se carga en la primera petición | RNF01 (2-5 s) | P0 | Precargar el modelo al arrancar el servidor |
| 11 | La lista de alertas del reponedor no se actualiza sola | CU02, RF05 "tiempo real" | P0 | Recarga automática de la página de alertas cada 60 s (sin push todavía) |
| 12 | Dashboard de disponibilidad por góndola (verde, amarillo, rojo, sin datos) e historial | CU03, RF05 | P1 | Ítem #43 |
| 13 | Exportar reportes Excel, CSV y PDF | CU04, RF06 | P1 | Ítem #7 |
| 14 | Umbral configurable y cámaras asociadas a góndolas | CU05, RF07 | P1 | Ítem #44 |
| 15 | Los pesos `yolo26s` no están en el servidor; sin ellos la app analiza con lo que encuentre | RF02 | P1 | Copiarlos al volumen `/data` del CITT (#39) |
| 16 | Los correos (enlace para definir la contraseña) solo se imprimen en la consola | CU06 | P1 | Configurar SMTP en el servidor (#39) |
| 17 | Las fotos guardadas pueden mostrar clientes: RNF05 pide no guardar rostros ni datos personales | RNF05 | P1 | Ítem #45, para conversar con Walmart (#24) |
| 18 | HTTPS en el CITT: sin él la cookie de sesión viaja en claro | RNF04 | P1 | Cookies seguras detrás de HTTPS (#39) |
| 19 | Notificación push al reponedor y alerta de cámara defectuosa | CU02, CU01 1a | P2 | Backlog |
| 20 | Registro de auditoría (quién hizo qué), como en el mockup Admin-4 | Mockups | P2 | Backlog |
| 21 | Bandeja de usuarios con búsqueda y "último acceso", como en el mockup Admin-3 | Mockups | P2 | El último acceso ya existe (`last_login`); se muestra en la lista |

## Lo que ya cumple

- RF08/CU00: login con RUT o correo, bcrypt, vista por perfil, bloqueo
  tras 5 intentos fallidos.
- RF09/CU06: crear, editar y desactivar cuentas y asignar perfil; la
  contraseña la define el usuario con un enlace de un solo uso;
  desactivar cierra las sesiones.
- CU01 desde la web: % libre de la góndola completa, alerta y foto
  anotada guardados en la base; análisis global cuando no hay repisas.
- RNF03: la app solo llama a `run_image()`; el pipeline sigue modular.

## Fuera del alcance de la app

- CU07 (evaluación por lotes) corre en `scripts/run_pipeline.py`.
- RF01 a intervalos de cámara (2-5 s): Walmart no comparte cámaras; hoy
  la ingesta es manual (subida de fotos).
