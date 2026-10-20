---
version: 1
slug: "web-templates-base-html"
primary_target: "web/templates/base.html"
related_targets: ["web/templates"]
---

# App web ShelfVision AI (todas las pantallas)

Scope: shell, login, alertas, análisis (lista y detalle), usuarios y páginas de error de `web/templates/`. Visitor mode: Operate.

Audience and job: Reponedor en el teléfono (tomar y completar alertas), Jefe de Salón en PC (subir fotos, ver estado), Administrador en PC (cuentas). Proof: foto anotada y franjas por repisa calculadas por el pipeline. Constraints: sin CDN (red de tienda / servidor CITT), sin marca Walmart, español de Chile, WCAG AA.

## Direction contract

THESIS: Cada góndola se ve como sus repisas de frente: el hueco se lee antes que el número. Rechaza el panel genérico de tarjetas con barra de progreso de un solo valor.

OWN-WORLD: Fleje de góndola. Barra superior grafito #1f2a30, fondo gris fleje #eef1f2, superficies blancas, texto grafito; hueco = rayado rojo #c8372b sobre rosado, acción verde azulado #0e7c7b, completada verde #1b7a4e. Archivo (ancho variable): narrow para ubicaciones y cifras, normal para texto. Radio 12px en paneles, 10px en botones.

STORY: El reponedor ve cuántas góndolas están en quiebre, cuál es la más urgente y dónde está, y la toma con un toque. El jefe sube una foto y ve en la franja qué repisas tienen huecos y quién atiende cada alerta.

FIRST VIEWPORT: Barra grafito de 56px con la marca y la navegación por perfil. Título con el conteo de quiebres abiertos (número en rojo). Debajo, una tarjeta por alerta: ubicación (Pasillo · Góndola) y % libre arriba, franjas por repisa a todo el ancho, botón de acción de 52px al pie. En PC, la lista de análisis es una tabla con una mini góndola (franjas apiladas) por fila.

FORM: Fleje de góndola, posición 1 de la lista ordenada (elección del usuario sobre la sorteada). seed: none (unavailable). Movimiento distintivo: las franjas por repisa dibujadas con la geometría real de los huecos del pipeline.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
