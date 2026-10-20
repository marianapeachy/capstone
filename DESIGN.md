---
name: ShelfVision AI
description: App web para detectar quiebres de stock en góndolas a partir de fotos
colors:
  graphite: "#1f2a30"
  graphite-soft: "#56656c"
  shelf-gray: "#eef1f2"
  surface: "#ffffff"
  hairline: "#d6dde0"
  gap-red: "#c8372b"
  gap-tint: "#f7d9d5"
  action-teal: "#0e7c7b"
  action-teal-deep: "#0a6463"
  action-tint: "#dcefee"
  action-on-graphite: "#6fd3cf"
  done-green: "#1b7a4e"
  done-tint: "#dcefe4"
  warn-amber: "#8a5a00"
  warn-tint: "#fbeccd"
typography:
  headline:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "30px"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.02em"
    fontVariation: "'wdth' 82"
  location:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "22px"
    fontWeight: 800
    lineHeight: 1.15
    fontVariation: "'wdth' 78"
  figure:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "32px"
    fontWeight: 800
    fontFeature: "'tnum'"
    fontVariation: "'wdth' 78"
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.45
    fontFeature: "'tnum'"
  label:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 600
rounded:
  control: "10px"
  panel: "12px"
  input: "8px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "20px"
  xl: "28px"
components:
  button-primary:
    backgroundColor: "{colors.action-teal}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.action-teal-deep}"
  button-complete:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.done-green}"
    rounded: "{rounded.control}"
    height: "52px"
  button-quiet:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.control}"
    height: "44px"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
    padding: "20px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.input}"
    height: "44px"
  topbar:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.surface}"
    height: "56px"
  state-active:
    backgroundColor: "{colors.gap-tint}"
    textColor: "#8f2219"
    rounded: "{rounded.pill}"
  state-in-progress:
    backgroundColor: "{colors.action-tint}"
    textColor: "{colors.action-teal-deep}"
    rounded: "{rounded.pill}"
  state-done:
    backgroundColor: "{colors.done-tint}"
    textColor: "#155f3d"
    rounded: "{rounded.pill}"
---

# Design System: ShelfVision AI

## Overview

**Creative North Star: "El fleje de góndola"**

El fleje es la tira del borde de cada repisa: lo primero que mira quien repone. El sistema dibuja cada góndola como sus repisas vistas de frente, una franja por repisa, con el producto en grafito y cada hueco rayado en rojo en su posición real, calculada por el pipeline. El hueco se lee antes que el número: la pregunta "¿hay quiebre?" se responde de un vistazo, y el porcentaje la confirma.

Es una herramienta de trabajo: barra grafito, fondo gris fleje, paneles blancos y una sola familia tipográfica (Archivo) que se angosta para ubicaciones y cifras. La densidad es de app diaria en escritorio y de tarjetas grandes en el teléfono, porque el reponedor la usa de pie en el pasillo con una mano ocupada. La interfaz es clara en ambos casos (luz de supermercado y de oficina) y no lleva marca de Walmart: la identidad es propia de ShelfVision AI.

**Key Characteristics:**
- Una franja por repisa, con huecos en su geometría real, como pieza central de cada vista.
- Rojo reservado para hueco y quiebre; verde azulado para acciones; verde para lo completado.
- Archivo variable: ancho normal para leer, angosto (78-82%) para ubicaciones y cifras.
- Objetivos táctiles de 44 px como mínimo y 52 px en las acciones del teléfono.
- Estilos, fuente e íconos servidos desde la propia app, sin CDN.

## Colors

Neutros fríos tomados del metal y la tira de la góndola, con tres colores de estado que siempre tienen un trabajo.

### Primary
- **Verde azulado de acción** (action-teal): botones de acción ("Tomar alerta", "Analizar", "Nuevo usuario"), foco del teclado, cursor y la marca "AI". Sobre la barra grafito se usa su versión clara (action-on-graphite) para la pestaña activa.

### Secondary
- **Rojo hueco** (gap-red): el rayado de los huecos en el fleje, los porcentajes de repisas y góndolas en quiebre, el conteo de quiebres del título y el contador de alertas de la barra. Su versión clara (gap-tint) es el fondo del estado "Activa" y de los errores.

### Tertiary
- **Verde completado** (done-green): el botón "Marcar repuesta" y el estado "Completada" o "Activa" de una cuenta.

### Neutral
- **Grafito** (graphite): barra superior, texto principal y el producto en las franjas del fleje.
- **Grafito suave** (graphite-soft): texto secundario, encabezados de tabla y rótulos de repisa.
- **Gris fleje** (shelf-gray): fondo de la página.
- **Blanco** (surface): paneles, tarjetas e inputs.
- **Línea fina** (hairline): divisiones de filas de tabla.

### Named Rules
**The Red Means Gap Rule.** El rojo solo marca huecos y quiebres. Nunca se usa para decorar ni para acciones; un botón destructivo futuro usa otro tratamiento.

**The Never Color Alone Rule.** Todo estado de color va con texto: el fleje va junto al % libre de la góndola y cada pastilla dice su estado.

## Typography

**Display Font:** Archivo (con system-ui)
**Body Font:** Archivo (con system-ui)

**Character:** Una sola familia de ancho variable. Angosta y gruesa para ubicaciones ("Pasillo 3 · Góndola 14B") y cifras ("39% libre"); normal para el texto. Cifras tabulares en toda la app.

### Hierarchy
- **Headline** (800, 30px, 1.15, ancho 82%): título de cada página; el conteo de quiebres va en rojo.
- **Location** (800, 22px, ancho 78%): ubicación de la góndola en tarjetas y paneles.
- **Figure** (800, 32px, ancho 78%): % libre de la góndola en tarjetas y detalle.
- **Body** (400, 16px, 1.45): texto, formularios y tablas (15px en tablas).
- **Label** (600, 13px): encabezados de tabla, rótulos de repisa y pastillas de estado.

### Named Rules
**The Narrow For Where Rule.** El ancho angosto es para dónde y cuánto (ubicación, porcentaje), nunca para párrafos.

## Layout

Contenedor centrado de 1180 px con márgenes de 20 px (12 px en el teléfono). Encabezado de página con título y acción principal a la derecha; debajo, paneles. Las alertas van en una grilla de tarjetas de 320 px mínimo que se alinea arriba; en el teléfono, una columna. El detalle de un análisis divide foto (3 partes) y fleje con datos (2 partes), y se apila bajo 760 px. En el teléfono la navegación muestra solo texto, se ocultan las columnas secundarias de las tablas (`hide-phone`) y el estado de la alerta se muestra bajo la ubicación.

## Elevation & Depth

Profundidad mínima con una sola sombra suave para paneles y tarjetas; sin bordes alrededor de los paneles. La tarjeta de la alerta que atiende el usuario agrega un anillo de 2 px verde azulado.

### Shadow Vocabulary
- **Panel** (`box-shadow: 0 1px 2px rgb(31 42 48 / .06), 0 6px 18px rgb(31 42 48 / .07)`): paneles, tarjetas de alerta y foto del detalle.

### Named Rules
**The One Elevation Rule.** Un panel se separa con sombra o con línea, nunca con ambas.

## Shapes

Esquinas suaves y constantes: 12 px en paneles, 10 px en botones, 8 px en inputs, pastillas redondas para estados y contadores. Las franjas del fleje tienen 3 px de radio (1 px en miniatura). La marca es una góndola de frente con un hueco rojo, dibujada como geometría simple.

## Components

### Buttons
- **Shape:** esquinas suaves (10px), alto 44px; 52px a todo el ancho en las tarjetas del teléfono.
- **Primary:** verde azulado con texto blanco; ícono de Phosphor a la izquierda.
- **Hover / Focus:** se oscurece en 150 ms; al presionar se reduce a 98%; anillo de foco de 3px verde azulado.
- **Complete:** blanco con borde y texto verde ("Marcar repuesta").
- **Quiet:** blanco con borde de línea fina (Cancelar, Editar, el selector de archivo).
- **Busy:** al enviar una foto el botón se desactiva y dice "Analizando…".

### Cards / Containers
- **Corner Style:** 12px.
- **Background:** blanco sobre gris fleje.
- **Shadow Strategy:** sombra de panel (ver Elevation & Depth).
- **Internal Padding:** 20px (28px en login).

### Inputs / Fields
- **Style:** borde de 1.5px gris azulado, fondo blanco, 8px de radio, 44px de alto; etiqueta arriba, ayuda y error abajo.
- **Focus:** borde verde azulado con halo de 3px en su tono claro.
- **Error:** texto rojo oscuro bajo el campo; errores generales en un bloque rosado sobre el formulario.

### Navigation
- **Style:** barra grafito de 56px fija arriba, con la marca, las secciones del perfil y el usuario con su perfil. La sección actual se marca con un subrayado de 3px verde azulado claro. Alertas lleva un contador rojo de alertas abiertas. En el teléfono se ocultan el nombre de la marca, los íconos de sección y el nombre del usuario.

### Fleje (signature component)
Una fila por repisa: rótulo (R1) y franja grafito con cada hueco rayado en rojo en su posición y ancho reales. No lleva % ni alerta por repisa: desde el 2026-10-19 se informan solo los de la góndola completa, que van junto al fleje. Tres tamaños: normal (16px), grande en el detalle (22px) y denso (10px) cuando la góndola tiene más de 8 repisas. En miniatura (tablas) las franjas se apilan en 34px de alto y el hueco es rojo plano, sin rayado. Lleva un `aria-label` con la cantidad de huecos de cada repisa.

### Estado vacío
Ícono, título y una frase que explica cómo se llena la vista ("Sin quiebres abiertos", "Todavía no hay análisis").

## Do's and Don'ts

### Do:
- **Do** mostrar el fleje junto al % libre de la góndola: el hueco antes que el número.
- **Do** dejar el fleje como geometría: nunca agregarle % ni alerta por repisa.
- **Do** escribir la ubicación como "Pasillo N · Góndola X" en el ancho angosto.
- **Do** dar a cada acción del teléfono 52px de alto y todo el ancho de la tarjeta.
- **Do** servir fuentes, íconos y estilos desde `web/static/`, sin CDN.

### Don't:
- **Don't** usar rojo fuera de huecos y quiebres.
- **Don't** usar el rayado como textura de fondo: solo marca huecos medidos, y en miniatura va plano.
- **Don't** mostrar un estado solo con color, sin texto.
- **Don't** usar la marca, el logo ni el azul y amarillo de Walmart.
