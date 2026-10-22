# Cambios en los C.U y diagramas por la app web (#28)

**Aplicados el 2026-10-21 (ítem #42)** en las plantillas, en las fuentes
Mermaid (incluidas las nuevas de CU00 y del diagrama de arquitectura) y
en sus PNG. Este documento queda como registro de qué cambió y por qué.

La app web (`web/`, ítem #28, 2026-10-18) se construyó con Django y
sesiones, no con la API FastAPI/Flask + JWT + React del diseño de la Fase
1 (justificación en el README, "Estrategia Algorítmica y Arquitectura").
Este documento lista qué hay que cambiar en las plantillas de C.U
(`Anexos/Diseño/Plantilla de C.U 0X.docx`), en sus diagramas de secuencia
(fuentes en `Anexos/Diseño/Diagramas fuente (Mermaid)/`) y en el diagrama
de arquitectura, para rehacerlos en el ítem #42.

## Cambio general (aplica a todos los diagramas)

| Diseño de la Fase 1 | App web actual |
| --- | --- |
| "Dashboard Web (Frontend)" en React + Tailwind | Páginas HTML generadas por Django (plantillas en `web/templates/`, estilo Pico CSS) |
| "API Backend" con rutas REST (`/api/v1/...`) y respuestas JSON | Vistas de Django que reciben formularios y devuelven páginas; no hay API REST |
| Token JWT en cada llamada | Sesión de Django: cookie firmada `HttpOnly`, guardada en el servidor |
| Errores HTTP (401, 400) mostrados por el frontend | El formulario se vuelve a mostrar con el mensaje de error; 403 si el perfil no tiene permiso |
| "Base de Datos (JWT/Usuarios)" | SQLite: usuarios y perfiles (grupos de Django) y análisis |

En los diagramas, los participantes "Dashboard Web" y "API Backend" o
"Servicio de ..." pasan a ser uno solo: "App web (Django)".

## CU00 - Autenticar usuario

Plantilla `Plantilla de C.U 00.docx` y diagrama `Diagrama C.U 00.png`
(sin fuente `.mmd`: hay que crearla).

| Dice hoy | Cambiar a |
| --- | --- |
| Paso 5: "El sistema genera un token de sesión seguro (JWT) codificando el Rol del usuario" | "El sistema abre una sesión segura vinculada al usuario y su rol" |
| Paso 6: Reponedor -> Vista de Alertas; Jefe de Salón -> Dashboard de Métricas; Admin -> Panel Global | Reponedor -> Alertas; Jefe de Salón -> Análisis (hasta que exista el dashboard, CU03; desde el 2026-10-22, #43: Góndolas); Administrador -> Gestión de usuarios (hasta que exista un panel global) |
| Excepción 4a: bloquea la cuenta tras 5 intentos | Igual, y precisar: la cuenta queda inactiva y solo el Administrador la reactiva (CU06) |
| Diagrama, paso 1: "Ingresa correo y contraseña" | "Ingresa RUT o correo y contraseña" (como ya dice la plantilla) |
| Diagrama, pasos 2 y 5: `POST /api/v1/auth/login`, "Retorna Token JWT + Perfil" | "Envía el formulario de login" y "Abre la sesión y redirige según el rol" |
| Diagrama, paso 8: "HTTP 401 Unauthorized" | "Muestra 'Credenciales incorrectas. Intente nuevamente.'" |
| Participante "Base de Datos (JWT/Usuarios)" | "Base de Datos (Usuarios)" |

## CU01 - Ingestar y analizar imagen

Plantilla y `Diagrama C.U 01.mmd`.

- Agregar un segundo origen de la foto: el Administrador o el Jefe de
  Salón la sube desde la app web (página "Análisis"), indicando el
  pasillo y la góndola. El participante
  "Cámara de sala / lote de fotos" queda como "Cámara de sala, lote de
  fotos o carga desde la app web".
- Lo que se guarda en la base: % libre de la góndola completa,
  alerta sí/no, la foto anotada y quién la subió. Las fotos solo se ven
  con sesión iniciada.
- El `opt` de cámara defectuosa (colores imposibles) sigue sin
  implementar; mantenerlo como opcional.

## CU02 - Notificar alerta de quiebre

Plantilla y `Diagrama C.U 02.mmd`.

- La alerta se ve en la página "Alertas" de la app web (los tres
  perfiles, pensada para el teléfono), que se recarga sola cada minuto.
  Los estados Activa, En proceso y Completada ya existen. Precisar: una
  góndola tiene a lo más una alerta abierta; una foto nueva con quiebre
  reemplaza a la anterior (en vez de consolidar por 15 minutos) y una
  foto sin quiebre confirma la reposición y la cierra.
- No hay notificación push: la plantilla debe marcarla como pendiente.

## CU03 - Dashboard de disponibilidad

Plantilla y `Diagrama C.U 03.mmd`. Sin implementar. Al rehacerlo:

- Cambiar `GET /api/v1/gondolas/status (token JWT)` y
  `GET /api/v1/gondolas/{id}` por "Abre la página de góndolas" y "Abre
  el detalle de la góndola".
- Unir "Dashboard Web" y "API Backend" en "App web (Django)".

## CU04 - Exportar reporte

`Diagrama C.U 04.mmd`. Sin implementar. Cambiar
`POST /api/v1/reports/generate` por "Pide el reporte (formulario)"; el
archivo (Excel, CSV o PDF) se descarga como respuesta de esa página.

## CU05 - Configurar cámara y umbrales

`Diagrama C.U 05.mmd`. Sin implementar. Cambiar
`PUT /api/v1/config/cameras/{id}`, "400 Umbral inválido" y "200 OK" por
"Guarda el formulario", "El formulario muestra 'Umbral inválido'" y
"Muestra 'Parámetros actualizados'". Unir "Panel de Configuración Web" y
"API Backend" en "App web (Django)".

## CU06 - Gestionar cuentas y roles

Plantilla y `Diagrama C.U 06.mmd`.

| Dice hoy | Cambiar a |
| --- | --- |
| Diagrama, paso 2: `POST /api/v1/users (datos + rol)` | "Envía el formulario del usuario (datos + rol)" |
| Participantes "Panel de Usuarios Web" y "Servicio de Usuarios" | "App web (Django)" |
| "Servicio de Correo" envía el enlace de un solo uso | Igual. Precisar que en desarrollo el correo se imprime en la consola del servidor; falta configurar SMTP para enviarlo de verdad |
| Nota: contraseña con hash bcrypt | Igual (Django con `BCryptSHA256PasswordHasher`) |
| Flujo 3a: desactivar "invalida inmediatamente sus tokens de sesión activos" | "cierra inmediatamente sus sesiones activas" (Django revisa en cada petición que la cuenta siga activa) |
| CRUD | Precisar que las cuentas no se borran, se desactivan, para no perder el historial (quién hizo cada análisis) |
| Lista de usuarios: RUT, Nombre, Correo, Rol, Estado | Igual |

## CU07 - Evaluar el sistema con un lote

Sin cambios: corre por `scripts/run_pipeline.py --annotations`, no por la
app web.

## Diagrama de arquitectura (`Anexos/Diseño/Diagrama de arquitectura/`)

- Capa 3: "API Backend Service - Python FastAPI/Flask" -> "App web Django
  (vistas, ORM, migraciones)"; "Validación JWT / Bcrypt" -> "Sesiones +
  bcrypt"; "Base de Datos" -> "SQLite (volumen /data en Docker)".
- Capa 4: "Dashboard Web React + Tailwind CSS" y "REST API JSON / HTTP"
  -> "Plantillas HTML de Django (servidas por la misma app)".
- Capa 2: "Detector Base YOLOv8" -> "Detector YOLO26" (ya estaba
  desactualizado).
- "Panel Admin: Configuración Cámaras ROI" -> sin ROI (la segmentación es
  automática; ver Notas de `PROGRESS.md`).
- "MVP Nivel 2: Evaluación Umbral Crítico < 30%" -> "Alerta con espacio
  libre >= 30%" (criterio decidido 2026-09-30).
