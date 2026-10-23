# Auditoría de seguridad por vulnerabilidades recientes (ítem #57)

Fecha: 2026-10-22. Responsable: Francisco. Pedido: revisar las
vulnerabilidades publicadas la semana del 2026-10-19 en distintos
lenguajes y librerías, y ver si alcanzan a la app web.

## Cómo se hizo

1. Búsqueda de las vulnerabilidades de la semana (Python, Django, Pillow,
   PHP, Node.js, Java y otras).
2. Contraste con lo que usamos: `requirements.txt`, el `Dockerfile` y el
   CI.
3. `pip-audit` (base OSV/PyPI) sobre el entorno del proyecto, para no
   depender de blogs.

Cada hallazgo dice de qué fuente sale. Las páginas agregadoras de CVE
(strix.ai, dailycve, blogs de resumen) pueden traer datos erróneos y los
CVE recientes aún no tienen análisis del NVD: la fuente que manda es el
aviso del proyecto o `pip-audit`.

## Lo que sí nos alcanza

### Pillow 12.3.0: corregido (la subida de fotos lo usa)

- **Dónde**: `PhotoForm` (`web/forms.py`) usa `forms.ImageField`, y Django
  valida con Pillow cada archivo que sube un usuario. Es entrada no
  confiable, con una cuenta de Reponedor basta. Pillow no estaba en
  `requirements.txt`: llegaba por otra dependencia, así que nada impedía
  quedarse en una versión vieja.
- **Qué**: Pillow 13.0.0 (2026-10-16) corrige unas 35 vulnerabilidades,
  según sus notas de versión: dos críticas de decodificador (almacenamiento
  nativo reutilizado tras cambios de modo; desbordamiento del decodificador
  JPEG con líneas más anchas que el tile), trece altas (TIFF, WMF/EMF,
  OpenJPEG, PDF, bucle sin límite con cabeceras Exif repetidas) y varias
  medias de agotamiento de memoria o CPU (BMP, GIF, MSP, APNG). `pip-audit`
  reporta 35 avisos para 12.3.0, todos con arreglo en 13.0.0.
- **Exposición real**: las que corren al abrir y validar una imagen
  (JPEG, TIFF, BMP, GIF, MSP, Exif) son alcanzables desde la subida de
  foto. Las de PDF/EPS y de funciones que no llamamos (`Image.merge`,
  `quantize`, guardar TIFF) no, pero no hay que depender de eso.
  La foto se valida con Pillow y después se decodifica con OpenCV
  (`web/views.py`, `cv2.imdecode`), que no se ve afectado.
- **Arreglo**: `pillow>=13.0` en `requirements.txt` (13.0 ya no admite
  Python 3.10; usamos 3.13). Entorno actualizado, 255 tests pasan.
- **Lo que queda**: Pillow 13 solo hay que subirlo en cada PC (`pip
  install -r requirements.txt`) y en la imagen Docker al reconstruirla.

### certifi 2026.7.22: corregido

- **Qué**: incidente de la CA emSign (eMudhra). Python 3.13.17 (2026-10-21)
  trae certifi 2026.10.19 por eso, y `pip-audit` reporta PYSEC-2026-4320
  para la versión anterior.
- **Exposición**: certifi lo trae `requests`, que usa
  `scripts/download_datasets.py` (descarga de datasets). La app web no
  hace conexiones salientes con él.
- **Arreglo**: `certifi>=2026.10.19` en `requirements.txt`.

### setuptools 78.1.0 (solo el entorno local)

`pip-audit` reporta PYSEC-2025-49 y PYSEC-2026-3447. No está en
`requirements.txt` ni en la imagen Docker (`python:3.13-slim` no lo
trae); solo está en el `.venv` local. No toca la app. Se puede subir con
`pip install -U setuptools` en cada PC.

## Lo que ya estaba cubierto

- **Django 6.1.2**: la versión que usamos ya trae el paquete de seguridad
  del 2026-10-06 (CVE-2026-77050, -84429, -87890 y -87975, según el aviso
  de Django). Además, no usamos `django.contrib.gis` ni formsets con clave
  primaria editable. `requirements.txt` pide `django>=6.1,<7`, por lo
  que una instalación nueva ya recibe la corregida.
- **Python en el contenedor**: `python:3.13-slim-trixie` no fija el parche;
  una reconstrucción recibe 3.13.17 (2026-10-21). Las CVE de CPython de
  2026 que encontré (SNI/`SSLContext` de septiembre, `tarfile`) están
  corregidas en las versiones recientes; los detalles de varias vienen de
  agregadores y no pude confirmarlos en python.org.
- **`tarfile`**: `scripts/download_datasets.py` extrae con
  `filter="data"` y solo de fuentes fijas del proyecto; no es una entrada
  de usuarios. Con un Python reciente queda cubierto.

## Lo que no nos alcanza

PHP (CVE-2026-109618/-109619), Node.js (Brotli y otros 9), Java/JSSE,
Tomcat y GitLab: no están en la pila (Django, OpenCV, PyTorch, ultralytics,
gunicorn). Node corre solo en el runner de GitHub Actions, que mantiene
GitHub. El incidente de LiteLLM en PyPI tampoco: no lo usamos.

## No se pudo auditar

- **torch y torchvision**: vienen del índice de PyTorch (`+cu130` / CPU),
  que `pip-audit` no cubre. No encontré avisos de PyTorch, OpenCV ni
  ultralytics para la semana, pero la búsqueda fue mínima. Revisar los
  avisos de GitHub de cada proyecto antes de la instalación en el CITT (#39).
- **Imagen base Debian**: faltaría un escáner de imagen (Trivy o
  `docker scout`) sobre `shelfvision-ai`. Propuesto abajo.

## Pendiente

1. Un escáner de la imagen en el CI (`trivy` o `docker scout`) y
   `pip-audit` sobre `requirements.txt`. Se cruza con #54 (acciones del
   CI fijadas por commit: hecho el 2026-10-23).
2. La configuración de la app (DEBUG apagado por defecto, cookies seguras,
   usuario sin privilegios en el contenedor) es el ítem #50.
3. Si se instala en el CITT (#39), repetir `pip-audit` ese día: la lista
   cambia cada semana.
