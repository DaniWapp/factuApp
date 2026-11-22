# Arquitectura y API de FacturApp

El navegador solo habla con Flask (frontend). Flask llama a la API de FastAPI (backend) desde el servidor, y solo la API habla con la base de datos `facturapp` (MySQL 8 o MariaDB).

```
Navegador -> Flask (puerto 5000) -> API FastAPI (puerto 8000, JSON) -> MySQL o MariaDB (puerto 3306)
```

Las referencias RN, RNF y HU corresponden a `02-requisitos.md`.

## 1. Capas del backend

```
backend/
├── app/
│   ├── main.py              Crea la aplicación FastAPI, registra los routers y los manejadores de errores
│   ├── core/                Configuración y seguridad que usa toda la API
│   │   ├── config.py        Lee el .env: datos de la base, clave del JWT y tiempo de sesión
│   │   ├── seguridad.py     Cifra y verifica contraseñas (bcrypt); crea y verifica tokens (JWT)
│   │   ├── dependencias.py  Obtiene el usuario actual desde el token y exige un rol
│   │   └── errores.py       Errores del negocio y el código HTTP de cada uno (404, 409...)
│   ├── db/                  Conexión a la base de datos
│   │   └── conexion.py      Abre la conexión con PyMySQL y maneja la transacción (COMMIT o ROLLBACK)
│   ├── schemas/             Forma de los datos que entran y salen, validada con Pydantic
│   ├── routers/             Rutas de la API: reciben la petición y devuelven la respuesta
│   ├── services/            Reglas del negocio: permisos finos, stock, estados e historial
│   └── repositories/        Consultas SQL de cada tabla; única capa que toca la base de datos
├── tests/                   Pruebas con pytest
├── .env                     Credenciales reales (no se sube a git)
├── .env.example             Las mismas variables, sin valores reales
└── requirements.txt         Librerías del backend con su versión exacta
```

| Capa | Responsabilidad |
|---|---|
| `core/` | Guarda lo que usa toda la API: la configuración, la seguridad (contraseñas y tokens), la verificación del usuario y su rol, y los errores. |
| `db/` | Abre la conexión con la base de datos y asegura que cada operación se guarde completa o no se guarde (RN-17). |
| `schemas/` | Define y valida la forma de los datos que llegan y salen, antes de tocar la base de datos. |
| `routers/` | Recibe cada petición HTTP, llama al service que corresponde y devuelve el código y el JSON de respuesta. |
| `services/` | Aplica las reglas del negocio (RN) y coordina los repositories dentro de una transacción. |
| `repositories/` | Contiene el SQL (PyMySQL, sin ORM); es la única capa que habla con las tablas. |

**Orden de las llamadas:** `routers` → `services` → `repositories` → base de datos. Cada capa solo habla con la siguiente: un router nunca escribe SQL y un repository nunca decide reglas del negocio (RNF-23).

## 2. Recorrido de una petición: "crear entrega"

**Historia:** HU-21, registrar una entrega total o parcial.
**Ejemplo:** el Admin entrega los 2 motores MOT-001 que faltan en la solicitud SOL-000002.
**Endpoint:** `POST /solicitudes/2/entregas`
**Datos que envía Flask (JSON):**

```json
{ "repuestos": [ { "repuesto_id": 5, "cantidad": 2 } ] }
```

### En el frontend (Flask)

1. **`frontend/src/templates/solicitudes/detalle.html`:** el Admin presiona "Registrar entrega", escribe las cantidades y confirma (RNF-09). El botón solo se muestra al Admin, pero eso es una comodidad, no la protección real.
2. **`frontend/src/controllers/solicitudes_controller.py`:** Flask recibe el formulario, toma el token de la sesión y arma el JSON.
3. **`frontend/src/services/api_cliente.py`:** Flask envía la petición a la API desde el servidor, con el encabezado `Authorization: Bearer <token>`.

### En la API (FastAPI)

4. **`app/main.py` → `app/routers/entregas.py`:** FastAPI encuentra la ruta `POST /solicitudes/{solicitud_id}/entregas`.
5. **`app/core/dependencias.py` y `app/core/seguridad.py` — permiso 1, quién es:** se verifica la firma y la vigencia del token y se obtiene el usuario. Si el token no es válido o venció, responde **401** (RNF-02).
6. **`app/core/dependencias.py` (`requiere_rol("admin")`) — permiso 2, qué puede hacer:** solo el Admin registra entregas. Si es la Oficina radicadora, responde **403** (RN-02).
7. **`app/schemas/entregas.py` (`EntregaCrear`):** Pydantic valida que haya al menos un repuesto, que las cantidades sean mayores que cero, con máximo 2 decimales, y que no se repita un repuesto. Si algo falla, responde **422** (RN-11, RN-15).
8. **`app/routers/entregas.py`:** el router llama a `registrar_entrega(...)` de `app/services/entregas_service.py`, con los datos y el usuario.
9. **`app/db/conexion.py`:** el service abre una transacción. Desde aquí, o se guarda todo o no se guarda nada (RN-17).
10. **`app/repositories/solicitudes_repo.py`:** se lee la solicitud con `SELECT ... FOR UPDATE`, que la bloquea mientras dura la operación. El service revisa que exista (si no, **404**), que esté abierta (RN-22) y que su contratista esté activo (RN-31); si no, responde **409**.
11. **`app/repositories/detalle_solicitud_repo.py`:** se leen las filas del detalle, también con bloqueo. El service revisa que cada repuesto pertenezca a la solicitud, que no se entregue más de lo pendiente (RN-16) ni más de lo apartado (RN-33, RN-34) y que los decimales correspondan a la unidad de medida (RN-12). Si algo falla, responde **409**.
12. **`app/repositories/repuestos_repo.py` — revisión del stock:** se lee el repuesto con `FOR UPDATE` y el service comprueba que `stock_almacen` alcance (RN-10). Si no alcanza, responde **409** con el mensaje "No hay stock suficiente de MOT-001. Disponible: …". El bloqueo evita que dos Admin entreguen el mismo stock al mismo tiempo.
13. **`app/repositories/consecutivos_repo.py`:** se bloquea el contador `REM`, se le suma 1 y se arma el número **REM-000003** (RN-18).
14. **`app/repositories/entregas_repo.py`:** se guarda la entrega en `entregas` (con el contratista de la solicitud, el usuario y la fecha automática) y sus repuestos en `detalle_entrega`.
15. **`app/repositories/detalle_solicitud_repo.py`:** se actualiza el detalle: entregada +2 y apartada −2.
16. **`app/repositories/repuestos_repo.py`:** se actualiza el repuesto: stock en almacén −2 y apartado −2.
17. **`app/repositories/movimientos_repo.py`:** se guarda el movimiento de inventario: tipo "entrega", cantidad −2 y el stock que quedó.
18. **`app/repositories/historial_repo.py`:** se guarda en la línea de tiempo de la solicitud: "Remisión REM-000003".
19. **`app/db/conexion.py`:** se hace **COMMIT**. En este momento actúan los CHECK de MySQL como red de seguridad: si algo se escapó del service (por ejemplo, un stock negativo), la base de datos lo rechaza y se hace **ROLLBACK**.
20. **`app/services/entregas_service.py`:** calcula el nuevo estado de la entrega (en el ejemplo, "Completa", RN-21) y devuelve el resultado.
21. **`app/routers/entregas.py` y `app/schemas/entregas.py` (`EntregaRespuesta`):** la API responde **201 Created** con un JSON que trae el número de remisión, el estado de la entrega y los repuestos entregados.

Si cualquier paso entre el 9 y el 19 falla, el service lanza un error definido en `app/core/errores.py`, se hace ROLLBACK y `app/main.py` lo convierte en el código HTTP y el mensaje que corresponden. **No se guarda nada.**

### De vuelta en Flask

22. **`frontend/src/controllers/solicitudes_controller.py`:** si recibe **201**, muestra "Entrega registrada. Remisión REM-000003 generada." y vuelve al detalle de la solicitud.
23. **El mismo archivo:** si recibe **409 o 422**, muestra el mensaje de error sin borrar lo que el usuario escribió (RNF-08); si recibe **401**, lo lleva a la pantalla de inicio de sesión.

### Dónde se revisan los permisos y el stock

| Qué | Dónde | Para qué |
|---|---|---|
| Permisos | Flask, paso 1: oculta el botón a quien no tiene el rol | Comodidad; no es seguridad |
| | **`app/core/dependencias.py`**, pasos 5 y 6: token y rol | Protección real, aunque alguien escriba la dirección a mano |
| Stock | **`app/services/entregas_service.py`**, pasos 11 y 12, con los datos bloqueados | Revisión principal, con un mensaje claro para el usuario |
| | **CHECK de MySQL**, paso 19 | Última barrera, por si el código tiene un error |

## 3. Lista de endpoints

### 3.1 Convenciones

- **Dirección base:** `http://localhost:8000`. Solo Flask la usa; el navegador nunca llama a la API.
- **Formato:** todo entra y sale en JSON, con nombres en español y sin tildes (`fecha_entrega`, `stock_almacen`).
- **Autenticación:** todas las rutas, excepto `POST /auth/login`, exigen el encabezado `Authorization: Bearer <token>`.
- **Errores:** siempre con la forma `{"detail": "mensaje para el usuario"}`. `detail` es el nombre que usa FastAPI por defecto; el mensaje va en español, con los textos de las historias.
- **Nada se borra:** no hay rutas DELETE. Desactivar es un `PATCH .../estado`, y retractar, anular, cerrar o reabrir son `POST` que registran el evento (RN-05, RN-26).
- **Roles:** "Todos" = Admin y Oficina radicadora.

### 3.2 Códigos de respuesta

| Código | Cuándo |
|---|---|
| 200 OK | Consulta o cambio correcto |
| 201 Created | Se creó un registro (solicitud, entrega, entrada...) |
| 401 Unauthorized | Sin token, token alterado o sesión vencida (RNF-02, RNF-03) |
| 403 Forbidden | El rol no tiene permiso (RN-02), o el usuario está desactivado al iniciar sesión (RN-01) |
| 404 Not Found | El registro no existe |
| 409 Conflict | Choca con una regla de negocio: repetido, sin stock, solicitud cerrada, etc. |
| 422 Unprocessable Entity | Datos con forma inválida: faltan campos, cantidad ≤ 0, decimales de más (validación de `schemas/`) |

Todas las rutas protegidas pueden responder **401**, y las que no son de "Todos" pueden responder **403**; por eso las tablas siguientes solo nombran los códigos propios de cada ruta.

### 3.3 Autenticación

| Método | Ruta | Rol | Para qué | HU | Fase | Respuestas propias |
|---|---|---|---|---|:---:|---|
| POST | `/auth/login` | Público | Iniciar sesión con correo y contraseña; devuelve el token y el rol | HU-01 | 1 | 200, 401 (datos incorrectos), 403 (desactivado) |
| GET | `/auth/yo` | Todos | Datos del usuario actual y su rol, para armar el menú | HU-03 | 1 | 200 |
| PUT | `/auth/contrasena` | Todos | Cambiar la propia contraseña, también la temporal | HU-04, HU-05 | 2 | 200, 409 (clave actual incorrecta o igual a la temporal), 422 |

Cerrar sesión (HU-02) no necesita ruta en la API: Flask borra su sesión. El cambio a la vista de Oficina (HU-06) también lo maneja Flask (PA-26).

### 3.4 Usuarios

| Método | Ruta | Rol | Para qué | HU | Fase | Respuestas propias |
|---|---|---|---|---|:---:|---|
| GET | `/usuarios` | Admin | Listar usuarios | HU-09 | 1 | 200 |
| POST | `/usuarios` | Admin | Crear usuario | HU-07 | 1 | 201, 409 (correo repetido), 422 |
| GET | `/usuarios/{id}` | Admin | Ver un usuario | HU-08 | 1 | 200, 404 |
| PUT | `/usuarios/{id}` | Admin | Editar un usuario | HU-08 | 1 | 200, 404, 409, 422 |
| PATCH | `/usuarios/{id}/estado` | Admin | Activar o desactivar | HU-10 | 1 | 200, 404, 409 (desactivarse a sí mismo o al último Admin, RN-32) |
| POST | `/usuarios/{id}/restaurar-contrasena` | Admin | Asignar una contraseña temporal | HU-11 | 2 | 200, 404 |

### 3.5 Catálogos

| Método | Ruta | Rol | Para qué | HU | Fase | Respuestas propias |
|---|---|---|---|---|:---:|---|
| GET | `/categorias` | Todos | Listar categorías | HU-12 | 1 | 200 |
| POST | `/categorias` | Admin | Crear categoría | HU-12 | 1 | 201, 409 (nombre repetido), 422 |
| PUT | `/categorias/{id}` | Admin | Editar categoría | HU-12 | 1 | 200, 404, 409, 422 |
| PATCH | `/categorias/{id}/estado` | Admin | Activar o desactivar | HU-12 | 1 | 200, 404, 409 (tiene repuestos activos, RN-06) |
| GET | `/repuestos` | Todos | Listar el catálogo **sin datos de stock**, para elegir repuestos en una solicitud | HU-13, HU-17 | 1 | 200 |
| POST | `/repuestos` | Admin | Crear repuesto (empieza con stock 0) | HU-13 | 1 | 201, 409 (código o nombre repetido), 422 |
| PUT | `/repuestos/{id}` | Admin | Editar repuesto (sin campo de stock, RN-09) | HU-13 | 1 | 200, 404, 409, 422 |
| PATCH | `/repuestos/{id}/estado` | Admin | Activar o desactivar | HU-13 | 1 | 200, 404 |
| GET | `/contratistas` | Todos | Listar contratistas, para elegir uno en una solicitud | HU-14, HU-17 | 1 | 200 |
| POST | `/contratistas` | Admin | Crear contratista | HU-14 | 1 | 201, 409 (cédula o NIT repetido), 422 |
| PUT | `/contratistas/{id}` | Admin | Editar contratista | HU-14 | 1 | 200, 404, 409, 422 |
| PATCH | `/contratistas/{id}/estado` | Admin | Activar o desactivar | HU-14 | 1 | 200, 404 |
| GET | `/equipos` | Todos | Listar equipos | HU-15 | 1 | 200 |
| POST | `/equipos` | Todos | Registrar equipo | HU-15 | 1 | 201, 409 (código repetido), 422 |
| GET | `/equipos/{id}/solicitudes` | Todos | Historial de solicitudes de un equipo | HU-16 | 2 | 200, 404 |

### 3.6 Inventario

| Método | Ruta | Rol | Para qué | HU | Fase | Respuestas propias |
|---|---|---|---|---|:---:|---|
| GET | `/inventario` | Admin | Stock en almacén, apartado, disponible y en espera de cada repuesto | HU-20 | 1 | 200 |
| POST | `/inventario/entradas` | Admin | Registrar una entrada al almacén; aparta para las solicitudes en espera (RN-33) | HU-19 | 1 | 201, 404, 409 (repuesto inactivo), 422 |
| POST | `/inventario/entradas/{id}/retraccion` | Admin | Retractar una entrada, con motivo | HU-32 | 1 | 200, 404, 409 (ese stock ya se entregó o está apartado, RN-27), 422 |
| GET | `/inventario/{repuesto_id}/movimientos` | Admin | Historial de movimientos de un repuesto | HU-27 | 2 | 200, 404 |

### 3.7 Solicitudes

| Método | Ruta | Rol | Para qué | HU | Fase | Respuestas propias |
|---|---|---|---|---|:---:|---|
| GET | `/solicitudes` | Todos | Listar solicitudes; en la fase 2 acepta filtros (`?estado=`, `?equipo_id=`, `?contratista_id=`, `?desde=`, `?hasta=`, `?buscar=`) | HU-18, HU-25 | 1 | 200 |
| POST | `/solicitudes` | Todos | Crear solicitud; aparta lo disponible y deja el resto en espera | HU-17 | 1 | 201, 409 (equipo, contratista o repuesto inactivo), 422 |
| GET | `/solicitudes/{id}` | Todos | Detalle: repuestos (solicitado, entregado, pendiente), remisiones y línea de tiempo | HU-18, HU-22 | 1 | 200, 404 |
| PUT | `/solicitudes/{id}` | Admin | Editar una solicitud sin entregas vigentes | HU-34 | 1 | 200, 404, 409 (tiene entregas, RN-29), 422 |
| POST | `/solicitudes/{id}/anulacion` | Admin | Anular, con motivo | HU-34 | 1 | 200, 404, 409 (tiene entregas o está cerrada), 422 |
| POST | `/solicitudes/{id}/cierre` | Todos | Marcar como reparado o devuelto (devuelto exige motivo; con pendientes exige confirmación) | HU-23 | 1 | 200, 404, 409 (ya cerrada, RN-22), 422 |
| POST | `/solicitudes/{id}/reapertura` | Admin | Reabrir una solicitud reparada o devuelta, con motivo | HU-35 | 1 | 200, 404, 409 (anulada o abierta, RN-30), 422 |
| PATCH | `/solicitudes/{id}/contratista` | Admin | Reasignar el contratista | HU-36 | 1 | 200, 404, 409 (contratista inactivo o solicitud cerrada) |
| POST | `/solicitudes/{id}/reemplazos` | Admin | Reemplazar un repuesto desactivado sin stock | HU-37 | 1 | 201, 404, 409 (el repuesto tiene stock o está activo, RN-34), 422 |

### 3.8 Entregas, remisiones y devoluciones

| Método | Ruta | Rol | Para qué | HU | Fase | Respuestas propias |
|---|---|---|---|---|:---:|---|
| POST | `/solicitudes/{id}/entregas` | Admin | Registrar una entrega total o parcial y generar su remisión (ver sección 2) | HU-21 | 1 | 201, 404, 409 (sin stock, más de lo pendiente, solicitud cerrada, contratista inactivo), 422 |
| POST | `/entregas/{id}/retraccion` | Admin | Retractar una entrega, con motivo | HU-31 | 1 | 200, 404, 409 (ya retractada o solicitud cerrada), 422 |
| GET | `/entregas/{id}/remision` | Todos | Datos de la remisión para verla e imprimirla | HU-24 | 1 | 200, 404 |
| GET | `/entregas/{id}/remision.pdf` | Todos | Descargar la remisión en PDF | HU-29 | 2 | 200, 404 |
| POST | `/solicitudes/{id}/devoluciones` | Admin | Registrar la devolución de repuestos no usados (también en solicitudes cerradas) | HU-33 | 1 | 201, 404, 409 (más de lo entregado, RN-28), 422 |

### 3.9 Inicio y reportes

| Método | Ruta | Rol | Para qué | HU | Fase | Respuestas propias |
|---|---|---|---|---|:---:|---|
| GET | `/inicio/resumen` | Todos | Solicitudes por estado y entregas pendientes; al Admin también le muestra stock bajo | HU-26 | 2 | 200 |
| GET | `/reportes/entregas-por-contratista` | Admin | Reporte por rango de fechas (`?desde=&hasta=`); con `?formato=csv` descarga el archivo | HU-30 | 2 | 200 |
| GET | `/reportes/repuestos-mas-usados` | Admin | Reporte por rango de fechas; con `?formato=csv` descarga el archivo | HU-30 | 2 | 200 |

### 3.10 Resumen

- **Total:** 45 rutas: 37 de la fase 1 y 8 de la fase 2.
- La documentación interactiva de todas las rutas la genera FastAPI en `http://localhost:8000/docs`.

## 4. Capas del frontend

### 4.1 Carpetas

La aplicación Flask sigue el patrón del prototipo: `create_app` y un Blueprint por módulo.

```
frontend/
├── src/
│   ├── __init__.py            create_app: crea la aplicación, lee el .env y registra los Blueprints (solo aquí)
│   ├── app.py                 Punto de arranque del frontend
│   ├── auth.py                Decoradores login_required y admin_required, que protegen las rutas de Flask
│   ├── controllers/           Un Blueprint por módulo: recibe la petición del navegador y responde con una página
│   │   ├── auth_controller.py        Iniciar y cerrar sesión
│   │   ├── inicio_controller.py      Página de inicio
│   │   ├── usuarios_controller.py
│   │   ├── categorias_controller.py
│   │   ├── repuestos_controller.py
│   │   ├── contratistas_controller.py
│   │   ├── equipos_controller.py
│   │   ├── inventario_controller.py
│   │   ├── solicitudes_controller.py Solicitudes, entregas, devoluciones y correcciones
│   │   └── remisiones_controller.py  Ver e imprimir remisiones
│   ├── services/
│   │   └── api_cliente.py     El único archivo que habla con la API: agrega el token y traduce las respuestas
│   ├── templates/             Plantillas Jinja2: layout.html y una carpeta por módulo
│   │   ├── layout.html        Estructura común: menú según el rol y mensajes
│   │   └── repuestos/         lista.html y formulario.html (igual en cada módulo)
│   └── static/                Archivos que el navegador descarga tal cual
│       ├── css/               CSS propio (sin Bootstrap)
│       ├── js/                JavaScript en módulos (ES modules)
│       └── img/               Imágenes y logo
├── .env                       Dirección de la API y clave de la sesión (no se sube a git)
├── .env.example               Las mismas variables, sin valores reales
└── requirements.txt           Librerías del frontend con su versión exacta
```

| Capa | Responsabilidad |
|---|---|
| `__init__.py` y `app.py` | Crean y arrancan la aplicación Flask y registran todos los Blueprints en un solo lugar. |
| `auth.py` | Revisa antes de cada página si hay sesión (`login_required`) y si el rol es Admin (`admin_required`); si no, redirige con un mensaje. |
| `controllers/` | Cada Blueprint recibe las peticiones de su módulo, pide los datos a `api_cliente.py` y devuelve la página que corresponde. |
| `services/api_cliente.py` | Es el único que habla con la API: arma la dirección, agrega el token de la sesión y convierte cada código de respuesta en datos o en un error claro. |
| `templates/` | Arman el HTML que ve el usuario a partir de los datos que les pasa el controller. |
| `static/` | Guarda el CSS, el JavaScript y las imágenes que el navegador descarga sin procesar. |

**Regla de capas:** ninguna plantilla ni controller llama a la API directamente: todo pasa por `api_cliente.py`. Así, si cambia la dirección de la API o la forma de enviar el token, solo se cambia un archivo.

**`auth.py` no reemplaza a la API:** ocultar una página en Flask es una comodidad para el usuario; la protección real la hace la API (`core/dependencias.py`, sección 2), que revisa el token y el rol en cada petición.

### 4.2 Recorrido: el Admin abre la página de repuestos

1. **Navegador:** el Admin hace clic en "Repuestos" en el menú, y el navegador pide `GET http://localhost:5000/repuestos`.
2. **`frontend/src/__init__.py`:** Flask encuentra la ruta `/repuestos`, que pertenece al Blueprint registrado en `controllers/repuestos_controller.py`.
3. **`frontend/src/auth.py` (`@login_required`):** revisa que la sesión tenga un token. Si no lo tiene, redirige a la pantalla de inicio de sesión.
4. **`frontend/src/auth.py` (`@admin_required`):** revisa que el rol guardado en la sesión sea Admin, porque gestionar repuestos es del Admin (HU-13). Si es la Oficina radicadora, la redirige a su inicio con el mensaje "No tiene permiso para ver esta página." (HU-03).
5. **`frontend/src/controllers/repuestos_controller.py`:** la función de la ruta pide la lista de repuestos a `api_cliente.py`.
6. **`frontend/src/services/api_cliente.py`:** lee la dirección de la API del `.env`, toma el token de la sesión y envía `GET http://localhost:8000/repuestos` con el encabezado `Authorization: Bearer <token>`.
7. **En la API:** `core/dependencias.py` verifica el token, `routers/repuestos.py` llama al service, y `repositories/repuestos_repo.py` hace el `SELECT`. La API responde **200** con la lista en JSON (sin datos de stock; el stock está en la página de Inventario).
8. **`frontend/src/services/api_cliente.py`:** según el código que recibe:
   - **200:** devuelve la lista al controller.
   - **401:** la sesión venció; avisa al controller, que borra la sesión y lleva al login con el mensaje "Su sesión expiró. Inicie sesión de nuevo." (HU-02).
   - **403:** avisa al controller, que lleva al inicio con "No tiene permiso para ver esta página.".
   - **La API no responde:** avisa al controller, que muestra un mensaje de error de conexión.
9. **`frontend/src/controllers/repuestos_controller.py`:** llama a `render_template("repuestos/lista.html", repuestos=lista)`.
10. **`frontend/src/templates/repuestos/lista.html`:** extiende `layout.html`, que arma el menú según el rol. Recorre la lista y crea una fila por repuesto con código, nombre, categoría, unidad de medida y estado; si la lista está vacía, muestra un mensaje en lugar de la tabla.
11. **Flask:** devuelve la página HTML al navegador con código **200**.
12. **Navegador:** descarga el CSS y el JavaScript de `static/` y muestra la tabla de repuestos.
