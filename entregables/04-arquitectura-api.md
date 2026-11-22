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
