# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Personal de una sala de alimentos no perecibles de un supermercado de
Walmart Chile, con tres perfiles (casos de uso CU00-CU07 en
`Anexos/Diseño/`):

- **Reponedor**: en el pasillo, de pie, con el teléfono en una mano y
  productos en la otra. Necesita saber qué góndola reponer primero, dónde
  está y avisar que la tomó o la terminó (CU02).
- **Jefe de Salón**: en un PC de la tienda. Sube o revisa análisis de
  góndolas, mira el estado de la sala y exporta reportes (CU01, CU03,
  CU04).
- **Administrador del Sistema**: en un PC. Gestiona cuentas y roles y
  configura cámaras y umbrales (CU05, CU06).

Uso mixto confirmado (2026-10-18): el Reponedor usa la app en el
teléfono; el Jefe de Salón y el Administrador, en escritorio.

Audiencias de evaluación: Walmart Chile (área de IA) en el demo, a más
tardar 2026-10-31, y los docentes de Duoc UC en la Evaluación 2 (semana
del 2026-10-28) y en la comisión.

## Product Purpose

Detectar quiebres de stock en góndolas a partir de fotos y avisar al
personal de sala. La pregunta central del cliente es si hay quiebre o
no: el sistema mide el espacio libre del frente de cada repisa y alerta
por góndola cuando el espacio libre llega al 30% (umbral configurable).
Éxito: el reponedor llega antes a la góndola vacía y el jefe ve el
estado de la sala sin recorrerla.

## Positioning

Pipeline híbrido explicable: visión clásica (OpenCV) para corregir la
imagen y segmentar góndola y repisas automáticamente, sin que nadie
dibuje zonas, más el detector YOLO26 sin NMS para productos apilados.
Funciona con fotos frontales, en ángulo o desde arriba. Walmart prefiere
un modelo que el equipo pueda explicar a uno con más rendimiento.

## Operating Context

- Las fotos llegan de cámaras de sala o de lotes; hoy se suben desde la
  app web. Walmart no comparte fotogramas reales de sus cámaras.
- Una alerta es por góndola, con el detalle de las repisas afectadas.
  Su ciclo (CU02): Activa, En Proceso (la tomó un reponedor),
  Completada; la siguiente captura confirma la reposición.
- Walmart evalúa por IoU contra una anotación a mano y valora el
  criterio de la solución; no exige un resultado perfecto.
- Se instala con Docker en un servidor de la universidad (CITT), sin
  saber si tiene GPU.

## Capabilities and Constraints

- Hecho: login con RUT o correo y vista por perfil (CU00), usuarios y
  roles (CU06), análisis de fotos con % libre de la góndola completa,
  alerta y foto anotada (CU01), lista de alertas.
- Pendiente: pasillos y góndolas como entidades, dashboard (CU03),
  reportes Excel/CSV/PDF (CU04), configuración de cámaras y umbrales
  (CU05), notificaciones push, alerta de cámara defectuosa.
- Stack: Django 6.1 + SQLite con plantillas HTML (decidido 2026-10-18,
  ver README). Sin API REST ni frontend aparte.
- Terminología: "góndola", "repisa" (nivel), "pasillo", "quiebre de
  stock", "espacio libre", "reposición". El umbral se expresa como
  espacio libre >= 30%, nunca como "disponibilidad < 30%".
- Profundidad de góndola fija de 25 cm; el análisis es 2D.

## Brand Commitments

- Nombre: **ShelfVision AI**, identidad propia del proyecto (confirmado
  2026-10-18). Sin logo, colores ni marca de Walmart en la app: el
  repositorio es público. Walmart aparece solo como cliente en el
  README.
- Idioma: español de Chile, trato directo y funcional.

## Evidence on Hand

- Mockups de la Fase 1 (evaluados): `Anexos/Diseño/Mockups/` (Admin,
  Dashboard y Mobile). Sus datos (KPIs, nombres, tiempos) son de
  ejemplo, no resultados reales.
- Fotos que se pueden mostrar a terceros: Kaggle supermarket-shelves
  (CC0), SHARD y Roboflow (CC BY 4.0). SKU-110K nunca se muestra.
- Métricas reales del detector: `PROGRESS.md` (#5, #6, #22). No inventar
  KPIs de negocio (tiempos de reposición, SLA): el sistema no los mide
  todavía.

## Product Principles

1. La pregunta es "¿hay quiebre?": cada pantalla responde eso primero.
2. Una acción por pantalla para el reponedor: ver la alerta, tomarla,
   terminarla.
3. Mostrar la evidencia: la foto anotada respalda cada alerta.
4. Honestidad de datos: solo cifras que el sistema calcula; lo que no
   existe se muestra como vacío, no se simula.
5. Explicable: el criterio (umbral, repisas, huecos) se ve en la
   interfaz.

## Accessibility & Inclusion

Uso en sala con luz de supermercado y una mano ocupada: objetivos táctiles
grandes, contraste alto y estados que no dependan solo del color (rojo y
verde siempre con texto). WCAG AA como mínimo.
