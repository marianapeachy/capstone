# Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile)

## 📌 Descripción General del Proyecto

Este repositorio contiene el código fuente, la documentación técnica y la arquitectura del sistema desarrollado para la asignatura **Proyecto de Título (APT122 / Capstone)** en **Duoc UC**, en colaboración con **Walmart Chile**.

El proyecto aborda la automatización de la auditoría de espacios en salas de venta de supermercados mediante algoritmos de **Visión Artificial (Computer Vision)**. La solución analiza capturas fotográficas de cámaras de seguridad para detectar en tiempo real la disponibilidad de stock y cuantificar los espacios vacíos en góndola ("quiebres de stock" e "inventarios fantasmas").

---

## 🎯 Definición del Alcance

### 1. Dominio de Aplicación
* **Categoría Seleccionada**: Góndolas de **Alimentos No Perecibles** (cajas, latas, frascos, bolsas).
* **Actualización de Alcance**: Se descarta de forma definitiva el monitoreo de cestas de panadería, enfocando la arquitectura exclusivamente en la complejidad visual de los estantes de no perecibles.
* **Desafíos Visuales del Entorno**:
  * **Alto ruido visual**: Variaciones abruptas de iluminación, reflejos en empaques plásticos/metálicos y sombras al fondo del estante.
  * **Perspectiva y lentes**: Distorsión óptica por ángulos oblicuos de cámaras de seguridad y lentes tipo *fisheye*.
  * **La Trampa del Apilamiento**: Diferenciación entre espacio libre útil para reposición y espacio vertical vacío donde no es posible apilar productos por fragilidad o geometría.

---

## 💡 Objetivos y Niveles de Solución

El proyecto contempla una estructura de dos niveles de solución para garantizar la viabilidad técnica:

| Criterio | Solución Óptima (Nivel 1) | MVP Alternativo (Nivel 2) |
| :--- | :--- | :--- |
| **Objetivo Principal** | Medición espacial y volumétrica exacta del espacio libre | Alerta macro por umbral binario de stock |
| **Métrica de Salida** | Centímetros o porcentaje exacto de espacio vacío por repisa | ¿Disponibilidad < 30% en la góndola? (Sí / No) |
| **Granularidad** | Segmentado nivel por nivel de la góndola (Nivel 1, 2, 3...) | Análisis global de la imagen |
| **Complejidad** | Alta (Segmentación espacial + Visión Computacional) | Media (Detección por umbral de píxeles / parches) |

---

## 🛠️ Requerimientos Funcionales (RF)

* **RF01 - Ingesta de Imágenes**: Procesamiento estático de fotogramas en formato imagen (tiempo de inferencia objetivo: 2 a 5 segundos por imagen).
* **RF02 - Detección de Espacios Vacíos**: Identificación de regiones sin producto dentro de las regiones de interés (ROI) correspondientes a la góndola.
* **RF03 - Cálculo de Disponibilidad**: Estimación cuantitativa del espacio libre (porcentaje/cm o clasificación por umbral <30%).
* **RF04 - Generación de Alertas**: Emisión de notificaciones prioritarias para el equipo de reposición cuando se detecte un quiebre de stock.
* **RF05 - Módulo de Reportería**: Exportación de datos analíticos auditados en formatos **Excel (.xlsx)**, **CSV** y **PDF**.

---

## 👥 Perfiles de Usuario

1. **Reponedor de Tienda**: Recibe alertas inmediatas en dispositivos móviles para acudir a los pasillos con quiebre crítico.
2. **Jefe de Salón / Supervisor**: Visualiza dashboards de disponibilidad por pasillo y exporta reportes periódicos de desempeño.
3. **Administrador de Sistema**: Configura planogramas, define zonas ROI de góndolas y gestiona usuarios.

---

## 🏗️ Estrategia Algorítmica y Arquitectura

* **Enfoque Híbrido**: Evaluación de modelos de extracción de características (**YOLO11**) combinados obligatoriamente con **Visión Computacional Clásica** (detección de bordes, transformaciones matriciales y filtros morfológicos) para mantener control matemático sobre el ruido visual.
* **Pipeline Modular**: Separación física de los componentes de *Pre-procesamiento*, *Inferencia de Modelo* y *Post-procesamiento*.
* **Código de Producción**: Desarrollo exclusivo en scripts modulares de Python (`.py`), descartando notebooks para la ejecución core.

---

## 📊 Estrategia de Datos y Evaluación

* **Dataset de Entrenamiento**: Ccuraduría propia mediante fuentes públicas open-source (ej. *Hugging Face Grocery Shelves*, *Kaggle Supermarket Shelves*) con estandarización estricta de coordenadas de anotación (`[x_min, y_min, x_max, y_max]`).
* **Prueba Ciega (Dataset Oculto)**: Evaluación iterativa contra un **Dataset Oculto** de Walmart Chile que contiene imágenes reales de sala con condiciones complejas no visibles para el equipo de desarrollo.

---

## 📁 Estructura del Repositorio

```text
.
├── docs/                   # Documentación de diseño, minutas y especificaciones
├── src/                    # Código fuente en scripts Python modulares
│   ├── preprocessing/      # Filtros de imagen, corrección ROI y pre-procesamiento
│   ├── models/             # Módulos de inferencia (YOLO11 / CV Clásico)
│   ├── postprocessing/     # Cálculo de métricas y lógica de umbrales (<30%)
│   └── reporting/          # Generadores de reportes (Excel, CSV, PDF)
├── data/                   # Instrucciones y scripts de preparación de datasets
├── tests/                  # Pruebas unitarias e integración
├── README.md               # Documentación principal del repositorio
└── requirements.txt        # Dependencias del proyecto
```

---

## 📅 Planificación y Cronograma (Carta Gantt)

* **Fase 1 (Semanas 1 - 4 / 20%)**: Inscripción, reunión con cliente, levantamiento de RF y definición de arquitectura.
* **Fase 2 (Semanas 5 - 16 / 50%)**: Desarrollo modular, integración, pruebas continuas en Dataset Oculto y Pre-examen.
* **Fase 3 (Semanas 17 - 18 / 30%)**: Ajustes finales, manuales de usuario/instalación y Exposición ante Comisión Evaluadora.

---

## 👨‍💻 Equipo de Desarrollo

* **Asignatura**: Proyecto de Título (APT122 / Capstone) - Duoc UC
* **Cliente**: Walmart Chile (Área de Inteligencia Artificial)
