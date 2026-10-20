# Análisis de resultados preliminares (ítem #34)

Análisis pedido para el informe intermedio (2026-10-21): los 10 mejores
y los 10 peores casos del sistema, y un análisis comparativo con
métricas. Medido el 2026-10-20 sobre `main` 07a5981 con el detector
`yolo26s` entrenado (#5).

## Método

- **Fotos**: las 45 de Kaggle *supermarket-shelves* (Humans in the
  Loop, CC0: se pueden mostrar). No se usaron para entrenar, así que
  miden el detector fuera de SKU-110K. Cada producto viene anotado a mano
  con su caja. La 035 es la misma foto que la 004: se cuenta una vez (44
  fotos únicas). Nunca SKU-110K (su licencia prohíbe mostrar sus fotos).
- **Sistema**: el pipeline completo, igual que en la aplicación web
  (`scripts/run_pipeline.py`, CPU, 4 hilos), con la evaluación por lotes
  de CU07:

  ```bash
  python scripts/run_pipeline.py "data/raw/supermarket-shelves/Supermarket shelves/images" \
      --annotations data/processed/annotations/kaggle_supermarket.csv \
      --out data/processed/analisis-34/kaggle --device cpu --threads 4
  ```

- **Resultado esperado**: la anotación hecha a mano medida con la misma
  segmentación y el mismo cálculo de disponibilidad (`measure_boxes()`).
  Así, la diferencia entre ambos se debe solo a la detección.
- **Métricas por foto** (`metrics.csv`): P, R y F1 de detección con IoU
  >= 0,5; IoU medio de los aciertos; % libre de la góndola completa del
  sistema y de la anotación; alerta (libre >= 30%) de ambos.
- **mAP del detector**: `scripts/train_detector.py val` sobre las mismas
  45 fotos convertidas a formato YOLO (`nms=False`, `max_det=1000`,
  `imgsz=1280`).
- **Ranking**: primero se separan las fotos donde la alerta coincide con
  la esperada. Dentro de cada grupo se ordenan por el error de % libre,
  con un ajuste por F1. Mejores: los 10 primeros, sin repetir escenas
  casi iguales. Peores: las 7 alertas equivocadas y las 3 fotos con mayor
  error de % libre.
- **Láminas**: `docs/analisis-resultados/<mejor|peor>-<foto>.jpg`, con la
  entrada, el resultado del sistema (huecos en rojo, contorno de las
  repisas medidas y cartel con la alerta y el % libre de la góndola) y el
  resultado esperado.

## Resumen de métricas

| Medición | Fotos | P | R | F1 | mAP50 | mAP50-95 | Alerta correcta | Error medio de % libre |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Detector en test de SKU-110K (#5, referencia) | 2.935 | 0,915 | 0,885 | - | 0,950 | 0,610 | - | - |
| Detector en Kaggle (Ultralytics `val`) | 45 | 0,843 | 0,644 | - | 0,713 | 0,423 | - | - |
| Sistema completo, todas | 44 | 0,889 | 0,555 | 0,684 | - | - | 84% (37/44) | 9,6 pts |
| Sistema completo, productos envasados | 36 | 0,900 | 0,713 | 0,796 | - | - | 92% (33/36) | 6,2 pts |
| Sistema completo, frutas y verduras sueltas | 8 | 0,783 | 0,156 | 0,260 | - | - | 50% (4/8) | 24,7 pts |

IoU medio de los aciertos: 0,82. **Tiempo por foto** (CPU i5-13400F, 4
hilos, 45 fotos de 5616 x 3744): mediana de 0,51 s (corrección 0,18,
segmentación 0,04, detección 0,27, disponibilidad 0,02). Cumple RF01
(2 a 5 s).

Errores de alerta: 6 falsas alertas (4 en fotos de frutas y verduras
sueltas) y 1 alerta perdida. Solo 1 de las 44 fotos tiene un quiebre
real según su anotación (la 011): este set mide sobre todo falsas
alertas, no la detección de quiebres.

## 10 mejores casos

| # | Foto | Escena | Sistema | Esperado | Detección | Por qué es exitoso |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [026](analisis-resultados/mejor-026.jpg) | Botellas de vidrio en filas, de frente, fondo oscuro | 2% libre, sin alerta | 2%, sin alerta | 92 de 91; P 0,99, R 1,00, IoU 0,88 | Productos separados y de igual tamaño; contraste alto con el fondo |
| 2 | [001](analisis-resultados/mejor-001.jpg) | Potes de snacks apilados en 5 repisas | 0%, sin alerta | 0%, sin alerta | 255 de 264; F1 0,96, IoU 0,72 | Encuentra casi todos los potes aunque estén apilados. El IoU más bajo se debe a que la anotación y el detector cortan distinto los potes de una pila |
| 3 | [027](analisis-resultados/mejor-027.jpg) | Latas en 2 repisas, poca luz | 0%, sin alerta | 0%, sin alerta | 65 de 61; F1 0,95, IoU 0,89 | Las latas llenan el frente; la poca luz no afecta porque el contraste es alto |
| 4 | [008](analisis-resultados/mejor-008.jpg) | Pasillo completo de abarrotes: 8 repisas y productos chicos (vista amplia) | 4%, sin alerta | 4%, sin alerta | 295 de 281; F1 0,95, IoU 0,88 | Góndola entera en la foto, como la vería una cámara de sala; ubica los mismos huecos chicos que la anotación |
| 5 | [017](analisis-resultados/mejor-017.jpg) | Cajas de cereal, de frente | 0%, sin alerta | 0%, sin alerta | 50 de 50; F1 0,94, IoU 0,89 | Cajas grandes y rectangulares, el caso típico de SKU-110K |
| 6 | [002](analisis-resultados/mejor-002.jpg) | Conservas muy densas (690 latas) | 0%, sin alerta | 0%, sin alerta | 714 de 690; F1 0,94, IoU 0,77 | Alta densidad: la cabeza sin NMS y `max_det=1000` evitan perder latas vecinas o cortar en 300 |
| 7 | [012](analisis-resultados/mejor-012.jpg) | Latas apiladas de colores repetidos | 0%, sin alerta | 0%, sin alerta | 313 de 317; F1 0,94, IoU 0,76 | Separa productos iguales que se tocan |
| 8 | [006](analisis-resultados/mejor-006.jpg) | Fruta picada en envases transparentes, con huecos reales | 16%, sin alerta | 15%, sin alerta | 52 de 59; P 1,00, R 0,88, IoU 0,79 | Mide un espacio libre parcial casi igual al esperado, con los huecos en la misma posición |
| 9 | [024](analisis-resultados/mejor-024.jpg) | Bolsas de snacks, poca luz y algo de ángulo | 0%, sin alerta | 0%, sin alerta | 46 de 53; P 0,98, R 0,85, IoU 0,78 | Las bolsas que no detecta están entre otras detectadas, así que no dejan un hueco de un producto de ancho |
| 10 | [021](analisis-resultados/mejor-021.jpg) | Cereales con huecos reales en las 2 repisas de abajo | 11%, sin alerta | 9%, sin alerta | 63 de 72; P 0,98, R 0,86, IoU 0,89 | Encuentra los dos huecos reales y no inventa otros |

Métrica o criterio de éxito: la alerta coincide con la esperada, el
error de % libre es de 2 puntos o menos y F1 >= 0,91.

## 10 peores casos

| # | Foto | Escena | Sistema | Esperado | Error | Posibles causas | Propuesta de mejora |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [007](analisis-resultados/peor-007.jpg) | Fruta suelta a granel en un exhibidor refrigerado, en ángulo | 51%, **alerta** | 0%, sin alerta | Falsa alerta; R 0,15 (60 de 378) | Detección: el detector aprendió productos envasados (SKU-110K) y no separa frutas sueltas; perspectiva | Fuera del alcance (no perecibles): declararlo así ante Walmart. Si se pide, otra clase "a granel" u ocupación por color y textura |
| 2 | [023](analisis-resultados/peor-023.jpg) | Frutas en mallas y pirámides | 44%, **alerta** | 0%, sin alerta | Falsa alerta; R 0,30 | Igual que 007; las pirámides no tienen una repisa por fila | Igual que 007 |
| 3 | [003](analisis-resultados/peor-003.jpg) | Refrigerador abierto de bebidas y jugos (envasados, dentro del alcance) | 41%, **alerta** | 1%, sin alerta | Falsa alerta; R 0,51 | Iluminación: la repisa de abajo queda en sombra y se ve desde arriba; reflejos en envases claros arriba a la derecha | Fine-tuning con fotos de refrigeradores; revisar la confianza mínima en zonas oscuras |
| 4 | [014](analisis-resultados/peor-014.jpg) | Verduras en bandejas plásticas y sueltas, refrigerado | 35%, **alerta** | 10%, sin alerta | Falsa alerta; R 0,26 | Productos sin forma de caja; reflejos del plástico | Fuera del alcance; igual que 007 |
| 5 | [033](analisis-resultados/peor-033.jpg) | Pimientos sueltos en cajones | 33%, **alerta** | 10%, sin alerta | Falsa alerta; R 0,33 | Igual que 007; repisas en ángulo | Fuera del alcance; igual que 007 |
| 6 | [020](analisis-resultados/peor-020.jpg) | Refrigeradores con puerta de vidrio, vista oblicua desde el pasillo | 34%, **alerta** | 11%, sin alerta | Falsa alerta; P 0,60, R 0,48 | Reflejos y desenfoque de la puerta en primer plano, que cuentan como huecos; perspectiva fuerte; marcos entre puertas | Excluir zonas desenfocadas (nitidez local) y acotar la góndola a la parte enfocada; tratar los marcos de puerta |
| 7 | [011](analisis-resultados/peor-011.jpg) | Estante de tienda con pocos productos y pared blanca (único quiebre real del set) | 27%, sin alerta | 39%, **alerta** | Alerta perdida; P 0,82, R 0,96 | Segmentación: con pocos productos por repisa, los niveles salen distintos a los de la anotación (una fila necesita al menos 3 productos), y la góndola, acotada a los productos detectados, cambia con 2 o 3 cajas; queda a 3 puntos del umbral | Con pocos productos, usar como niveles las repisas de la segmentación; revisar el acotado de la góndola |
| 8 | [005](analisis-resultados/peor-005.jpg) | Tomates a granel en cajones | 24%, sin alerta | 0%, sin alerta | 24 pts de error; R 0,01 (10 de 251) | Detección (fuera del alcance); la alerta coincide por azar | Fuera del alcance |
| 9 | [030](analisis-resultados/peor-030.jpg) | Verdulería en canastos | 21%, sin alerta | 2%, sin alerta | 19 pts de error; R 0,01 (21 de 546) | Detección (fuera del alcance) | Fuera del alcance |
| 10 | [028](analisis-resultados/peor-028.jpg) | Botellas de bebida muy densas; abajo solo se ven las tapas | 4%, sin alerta | 21%, sin alerta | 17 pts de error; R 0,27 (64 de 215) | Oclusión y ángulo: en las filas de abajo solo asoman las tapas y el detector no las ve. A ojo la góndola está llena, más cerca del 4% del sistema: la referencia también se equivoca, porque las cajas anotadas de las filas bajas no cubren todo el frente | Fine-tuning con botellas vistas desde arriba; set propio anotado con el criterio de cobertura (#32) |

## Análisis comparativo

**Dónde funciona bien.** Productos envasados vistos de frente o con
poco ángulo: cajas, latas, botellas, bolsas y potes, incluso muy densos
(690 latas en la 002) o con la góndola completa en la foto (008). Ahí la
precisión es alta (0,90) y el sistema acierta la alerta en 33 de 36
fotos, con un error medio de 6 puntos de % libre. La poca luz no afecta
si el contraste con el fondo es alto (027, 024). Cuando hay huecos
reales (006, 021), los ubica en la misma posición que la anotación.

**Patrones de error**:

1. **Recall de detección**: el detector pierde productos, no inventa.
   La precisión se mantiene (0,89) y el recall cae de 0,885 en SKU-110K
   a 0,644 en Kaggle (mAP50 de 0,950 a 0,713). Cada producto perdido
   queda como hueco, así que el error de detección **sobreestima** el
   espacio libre y produce falsas alertas (6 de los 7 errores de alerta).
   Las dos fotos que lo subestiman (011 y 028) se explican por los niveles
   y por la referencia, no por la detección. Ya estaba
   anticipado: con recall simulado de 0,8, las falsas alertas con la
   góndola llena suben a 11,7% (AV-02 en `docs/test-plan.md`).
2. **Frutas y verduras sueltas** (8 fotos): recall 0,16 y 4 de las 6
   falsas alertas. Están fuera del alcance (no perecibles); Kaggle las
   incluye.
3. **Vidrio, reflejos y desenfoque** en refrigeradores (020, y 003 por
   sombra): los marcos, letreros y zonas borrosas cuentan como huecos.
   Es la condición más parecida a una cámara de sala que falla dentro
   del alcance.
4. **Oclusión y ángulo desde arriba** (028): solo se ven las tapas.
5. **Pocos productos por repisa** (011): los niveles son inestables y el
   único quiebre real del set queda 3 puntos bajo el umbral.

| Factor pedido | Lo que se observó |
| --- | --- |
| Iluminación | Poca luz con buen contraste no afecta (024, 027); una repisa en sombra sí (003) |
| Perspectiva | La vista amplia de frente funciona (008); la oblicua desde el pasillo, con primer plano, falla (020) |
| Sombras | Repisa inferior del refrigerador (003) |
| Reflejos | Puertas de vidrio (020) y envases plásticos (014) |
| Oclusiones | Botellas que se tapan entre sí (028) |
| Calidad de imagen | Desenfoque del primer plano (020); todas las fotos son de alta resolución (5616 x 3744), mejor que una cámara de sala |
| Errores de detección | Recall 0,644 fuera de dominio; causa de casi todos los peores casos |
| Errores de segmentación | Niveles con pocos productos (011) |

**Limitaciones del análisis**: 44 fotos de banco de imágenes, más
nítidas que una cámara de sala; solo una tiene un quiebre real, así que
no mide bien la detección de quiebres (para eso: Roboflow Out Of Stock,
con huecos anotados, paso 3 del #33, y las fotos propias de #32); la
referencia sale de una anotación que a veces no cubre el frente (028).

**Acciones prioritarias**:

1. **Fine-tuning del detector** con fotos fuera de SKU-110K (envasados
   de Kaggle CC0, Roboflow y fotos propias de #32), separando fotos de
   entrenamiento y de prueba. El mAP50 (0,713) queda justo sobre el
   criterio del #33 (0,70), pero el recall en envasados (0,71) está lejos
   del 0,90 de DET-04, y es lo que más falsas alertas causa.
2. **Declarar fuera del alcance** las frutas y verduras a granel (en el
   informe, la demo y ante Walmart, #24) y evaluar en adelante solo
   envasados.
3. **Refrigeradores**: excluir zonas desenfocadas y los marcos de puerta.
4. **Pocos productos**: usar las repisas de la segmentación como niveles.
5. **Medir quiebres reales** con Roboflow y el set propio, para calcular
   cuántos quiebres detecta el sistema, no solo sus falsas alertas.
