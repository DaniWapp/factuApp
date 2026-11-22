# Propuesta del proyecto FacturApp

## 1. Diagnóstico

Se revisó el prototipo guardado en `_backup/original/ADSO-25T4-FacturApp-main.zip`: una aplicación Flask con Blueprints y plantillas Jinja2 que muestra pantallas de contratistas, repuestos, categorías y usuarios.

### Lo que existe y lo que falta

| Área | Lo que existe | Lo que falta |
|---|---|---|
| Estructura Flask | `create_app`, 5 Blueprints (home, clients, categories, products, users) y un `layout.html` común | Carpeta `static/`, archivo `requirements.txt` e instrucciones para ejecutar |
| Pantallas | Formulario y lista de contratistas, repuestos, categorías y usuarios | Pantallas de login, equipos, solicitudes, inventario y remisiones |
| Formularios | Campos visibles con estilos de Bootstrap | Envío de datos, validación y mensajes de éxito o error |
| Datos | Filas de ejemplo escritas a mano en las tablas | Base de datos (MySQL o MariaDB) con `schema.sql` y `seed.sql` |
| Backend | Nada | API FastAPI que guarde y consulte los datos |
| Seguridad | Nada | Login, roles (Admin y Oficina radicadora), contraseñas cifradas y archivo `.env` |
| Trazabilidad | Nada | Estados de la entrega de repuestos y de la solicitud, con historial |
| Diseño | Bootstrap 5 desde CDN | CSS propio según la dirección visual del proyecto |
| Pruebas | Nada | Pruebas con pytest |
| Documentación | README de dos líneas y `.gitignore` | README con objetivo, instalación y uso |

### Problemas encontrados en el código

1. **`create_app` está repetido:** `src/__init__.py` y `src/controllers/__init__.py` tienen la misma función, así que hay dos lugares que mantener para lo mismo.
2. **Los formularios no envían nada:** el botón "Guardar" es `type="button"` y el `<form>` no tiene `method` ni `action`, por eso los datos nunca llegan al servidor.
3. **No hay rutas para recibir datos:** los controllers solo muestran plantillas (GET); ninguno procesa un formulario (POST).
4. **Los datos están escritos a mano en el HTML:** las tablas muestran filas fijas, así que lo que se registre nunca aparecerá en la lista.
5. **No hay base de datos ni API:** el sistema no guarda información de ninguna forma.
6. **No hay login ni roles:** cualquier persona que abra la página puede ver y usar todas las pantallas.
7. **Mezcla de inglés y español:** el menú, las rutas y los Blueprints están en inglés ("Clients", "New Client") y el contenido en español, y la página declara `lang="en"`.
8. **Nombres que no coinciden con el negocio:** el módulo `clients` en realidad maneja contratistas y `products` maneja repuestos, lo que confunde al leer el código.
9. **Enlaces escritos de dos formas:** `list_categories.html` usa `url_for()` pero las demás plantillas escriben la ruta a mano (`/form_clients`), y si una ruta cambia esos enlaces se rompen.
10. **Pantallas con diseño distinto:** `home.html` y `list_categories.html` no usan el contenedor ni las clases de tabla que usan las demás, por eso se ven diferentes.
11. **El buscador del menú no funciona:** el formulario "Search" no tiene ruta que lo procese.
12. **"Home" siempre aparece activo:** el menú marca la misma opción como activa en todas las páginas.
13. **El repuesto mezcla catálogo e inventario:** el formulario pide "Cantidad" pero no pide código, que es el dato mínimo del catálogo junto con el nombre.
14. **Las categorías del formulario de repuestos están fijas:** las opciones del `<select>` están escritas a mano, así que una categoría nueva no aparecería.
15. **Campos sin validación:** ningún campo es obligatorio (`required`), por eso se podría guardar un registro vacío.
16. **Etiquetas no conectadas a sus campos:** los `<label>` no tienen `for` ni los campos `id`, lo que dificulta el uso con lectores de pantalla.
17. **Tablas sin `<thead>` ni `<tbody>`:** el encabezado y los datos no están separados, lo que afecta los estilos y la accesibilidad.
18. **La forma de ejecutar no es clara:** `src/app.py` importa `from src import create_app`, por eso falla si se ejecuta directamente con `python src/app.py` y no hay instrucciones que digan cómo hacerlo.
19. **`debug=True` está escrito en el código:** el modo de depuración debería venir de la configuración (`.env`) para no dejarlo activo por error.
20. **Dato de ejemplo dudoso:** en la columna "Ciudad" del contratista aparece "Portobon", que parece el nombre de una empresa y no una ciudad.

## 2. Problema y objetivo

### Problema

1. Las solicitudes de repuestos para reparar neveras se llevan hoy en un **Excel compartido**, sin un sistema que controle quién registra o cambia cada dato.
2. Por eso es difícil saber qué repuestos se entregaron, cuáles faltan, a qué contratista y para qué equipo.
3. Tampoco se sabe con facilidad si el equipo quedó reparado o se devolvió, ni cuánto stock queda en el almacén.

### Objetivo general

Desarrollar un sistema web que registre las solicitudes de repuestos para la reparación de neveras y permita hacer la trazabilidad de las entregas, totales o parciales, y del estado de cada solicitud, con control de inventario y remisión imprimible.

### Objetivos específicos

1. Registrar solicitudes con equipo, contratista, fecha de entrega y repuestos del catálogo.
2. Registrar entregas totales o parciales que descuenten el stock y generen su remisión.
3. Guardar el historial de cada cambio de estado: quién lo hizo y cuándo.
4. Controlar el acceso con un solo login y permisos por rol (Admin y Oficina radicadora).

## 3. Alcance

### Fase 1: MVP (el flujo completo, de la solicitud a la remisión)

1. **Login con roles:** iniciar y cerrar sesión con contraseña cifrada; cada rol ve solo sus pantallas y la API revisa los permisos en cada ruta.
2. **Gestión de usuarios (Admin):** crear, editar y listar usuarios; activarlos o desactivarlos (un usuario inactivo no puede entrar).
3. **Contratistas (Admin):** crear, editar, listar y desactivar; el dato único es la cédula o NIT.
4. **Catálogo de repuestos (Admin):** categorías y repuestos con código, nombre, categoría y unidad de medida; se desactivan en lugar de eliminarse.
5. **Equipos (neveras):** registrar y listar por código.
6. **Inventario básico:** stock en almacén, apartado, disponible y en espera por repuesto; el Admin registra las entradas al almacén; al crear una solicitud se aparta lo pedido (lo que falte queda en espera de mercancía); el stock baja con cada entrega y no se puede entregar más de lo apartado.
7. **Solicitudes:** crear una solicitud (equipo, contratista, fecha de entrega y uno o más repuestos con su cantidad), listarlas y ver su detalle.
8. **Registro de entregas (Admin), totales o parciales:** se puede entregar todo lo solicitado o solo una parte y completar después; el sistema muestra lo entregado y lo pendiente por cada repuesto.
9. **Estado de la solicitud:** Admin u Oficina radicadora marcan el equipo como reparado o devuelto.
10. **Historial:** cada entrega y cada cambio de estado queda guardado con quién lo hizo y cuándo, y se ve en el detalle de la solicitud.
11. **Remisión:** una por cada entrega (también por cada entrega parcial), con número consecutivo, fecha, contratista, equipo y repuestos con cantidades; se ve en pantalla y se imprime desde el navegador.
12. **Base técnica:** `schema.sql` y `seed.sql`, `.env.example`, README con cómo ejecutar y pruebas con pytest del login, los permisos y el registro de entregas.
13. **Corrección de errores (Admin, con motivo y sin borrar nada):** retractar entregas y entradas al almacén, registrar devoluciones de repuestos no usados, editar o anular solicitudes sin entregas, reabrir solicitudes cerradas, reasignar el contratista de una solicitud y reemplazar repuestos desactivados que no tienen stock.
14. **Confirmación:** toda acción que guarda, cambia o desactiva datos pide confirmación antes de ejecutarse.

### Fase 2: Mejoras

1. **Cuentas:** cada usuario cambia su propia contraseña y el Admin restaura contraseñas.
2. **Cambio de vista del Admin:** pasar a la vista de Oficina radicadora sin volver a iniciar sesión.
3. **Inicio con resumen:** solicitudes por estado, entregas pendientes y repuestos con poco stock.
4. **Filtros y búsqueda:** por estado, equipo, contratista y fechas, más el buscador del menú.
5. **Historial por equipo:** todas las solicitudes de una nevera.
6. **Inventario avanzado:** historial de movimientos (entradas y salidas) y alerta de stock mínimo.
7. **Remisión en PDF** para descargar.
8. **Reportes:** entregas por contratista y repuestos más usados, con exportación a Excel o CSV.
9. **Más pruebas** para todos los módulos.

### Lo que NO incluye

1. **Facturación:** no maneja precios, costos, impuestos ni facturas.
2. **Acceso de contratistas:** no tienen usuario ni inician sesión.
3. **Compras a proveedores:** no hay órdenes de compra ni gestión de proveedores.
4. **Notificaciones** por correo, WhatsApp o SMS.
5. **Recuperar la contraseña por correo:** la restaura el Admin.
6. **Firma electrónica** de la remisión: se firma en papel después de imprimirla.
7. **Varias bodegas o sedes:** hay un solo inventario.
8. **Agenda de técnicos o mantenimiento preventivo.**
9. **Integración con otros sistemas** (ERP, SAP, etc.).
10. **App móvil y publicación en internet:** el sistema corre en el equipo local, con MySQL de AppServ o MariaDB de XAMPP.

### Reglas de alcance

1. Al crear una solicitud el stock se aparta; el stock en almacén baja al registrar cada entrega.
2. La fase 1 debe estar completa y funcionando antes de empezar la fase 2.

## 4. Roles, permisos y módulos

### Roles

El sistema tiene dos roles: **Admin** y **Oficina radicadora**. Hay **un solo login para todos**: cada persona entra por la misma pantalla y el sistema le muestra las opciones según su rol. El contratista (técnico reparador) **no** es un usuario del sistema: es un dato que se registra en cada solicitud.

La columna "Fase" indica si la acción entra en el MVP (fase 1) o en las mejoras (fase 2), según la sección 3.

| Acción | Admin | Oficina radicadora | Fase |
|---|:---:|:---:|:---:|
| Iniciar y cerrar sesión | Sí | Sí | 1 |
| Crear y consultar solicitudes de repuestos | Sí | Sí | 1 |
| Registrar entregas de repuestos (totales o parciales) y cambiar su trazabilidad | Sí | No | 1 |
| Marcar la solicitud como equipo reparado o devuelto | Sí | Sí | 1 |
| Consultar y registrar equipos (neveras) | Sí | Sí | 1 |
| Registrar entradas de repuestos al almacén | Sí | No | 1 |
| Consultar el inventario (stock disponible) | Sí | No | 1 |
| Ver e imprimir remisiones | Sí | Sí | 1 |
| Gestionar catálogos: contratistas, categorías y repuestos | Sí | No | 1 |
| Crear, editar y listar usuarios | Sí | No | 1 |
| Activar y desactivar usuarios (un usuario inactivo no puede entrar; un Admin no puede desactivarse a sí mismo ni al último Admin activo) | Sí | No | 1 |
| Retractar entregas y entradas al almacén, con motivo | Sí | No | 1 |
| Registrar devoluciones de repuestos no usados | Sí | No | 1 |
| Reabrir solicitudes cerradas, reasignar contratistas y reemplazar repuestos desactivados | Sí | No | 1 |
| Editar o anular solicitudes sin entregas | Sí | No | 1 |
| Restaurar la contraseña de un usuario con una contraseña temporal | Sí | No | 2 |
| Cambiar su propia contraseña | Sí | Sí | 2 |
| Cambiar a la vista de Oficina radicadora sin volver a iniciar sesión | Sí | No aplica | 2 |

**Contraseña temporal:** cuando el Admin restaura una contraseña, el sistema asigna una contraseña temporal y obliga al usuario a cambiarla en su siguiente inicio de sesión.

### Módulos

Lo marcado con **(fase 2)** se construye después del MVP, según la sección 3.

| Módulo | Pantallas | Quién lo usa |
|---|---|---|
| Autenticación | Iniciar sesión y cerrar sesión; cambiar contraseña **(fase 2)** | Todos |
| Inicio | Página de inicio con las opciones del rol; resumen de solicitudes por estado y entregas pendientes **(fase 2)** | Todos |
| Usuarios | Lista, formulario, activar o desactivar; restaurar contraseña **(fase 2)** | Admin |
| Contratistas | Lista y formulario | Admin |
| Equipos (neveras) | Lista y formulario; detalle con el historial de solicitudes del equipo **(fase 2)** | Admin y Oficina |
| Categorías de repuesto | Lista y formulario | Admin |
| Repuestos (catálogo) | Lista y formulario; cada repuesto tiene como mínimo código y nombre | Admin |
| Inventario | Stock disponible por repuesto y entradas al almacén | Admin |
| Solicitudes | Lista, formulario nuevo y detalle con línea de tiempo; filtros de la lista **(fase 2)** | Admin y Oficina, según los permisos |
| Remisiones | Remisión de cada entrega de repuestos, para ver e imprimir | Admin y Oficina (la genera el Admin al registrar la entrega) |

### El módulo central: Solicitudes

1. **Nueva solicitud:** se elige el equipo (por su código) y el contratista, se indica la fecha de entrega y se agregan uno o más repuestos del catálogo con su cantidad.
2. **Lista:** muestra todas las solicitudes; los filtros por estado, equipo, contratista y fechas llegan en la **fase 2**.
3. **Detalle:** muestra los datos de la solicitud, sus repuestos y una línea de tiempo con cada cambio de estado (quién lo hizo y cuándo). Los botones de cambio de estado solo aparecen para el rol que tiene permiso.

### Del prototipo al proyecto

| Prototipo | Proyecto |
|---|---|
| `clients` | Contratistas |
| `products` | Repuestos (catálogo) |
| `categories` | Categorías de repuesto |
| `users` | Usuarios |
| No existe | Autenticación, equipos, solicitudes, inventario y remisiones |

## 5. Stack y arquitectura

### Cómo se conectan las partes

```
Navegador -> Flask (frontend, puerto 5000) -> API FastAPI (JSON, puerto 8000) -> MySQL o MariaDB (puerto 3306)
```

1. **El navegador solo habla con Flask.** El usuario nunca ve ni llama directamente a la API.
2. **Flask muestra las pantallas.** Recibe los formularios, se los envía a la API y guarda en su sesión el token del usuario que inició sesión.
3. **FastAPI aplica las reglas del negocio.** Valida los datos, revisa los permisos de cada rol, cambia los estados y guarda el historial.
4. **Solo FastAPI habla con la base de datos.** Flask nunca se conecta a la base de datos.

**No se usa Apache:** Flask y FastAPI traen su propio servidor (el servidor de desarrollo de Flask y Uvicorn).

Frontend y backend se trabajan **como si vivieran en servidores separados**: cada uno tiene su propio entorno virtual, su `requirements.txt`, su `.env` y su `.env.example`. El frontend solo conoce la dirección de la API, que lee de su `.env`.

### Stack y por qué

| Parte | Tecnología | Por qué |
|---|---|---|
| Frontend | Python 3.12, Flask 3 (Blueprints y `create_app`), Jinja2, HTML5, CSS3 propio, JavaScript (ES modules) | Flask es requisito académico y el prototipo ya usa Blueprints. El CSS propio permite el diseño sobrio definido para el proyecto. |
| Backend | FastAPI, Uvicorn, Pydantic v2 | Separa las reglas del negocio de las pantallas, valida los datos automáticamente y genera la documentación de la API en `/docs`. |
| Acceso a datos | PyMySQL con SQL directo | Se escriben las consultas a mano, lo que ayuda a aprender SQL y a ver exactamente qué se ejecuta. |
| Seguridad | PyJWT y bcrypt | El token (JWT) identifica al usuario en cada llamada a la API y bcrypt guarda las contraseñas cifradas. |
| Base de datos | MySQL 8 (de AppServ) o MariaDB (de XAMPP), modelo en MySQL Workbench | El MySQL de AppServ ya está instalado en el equipo de desarrollo; el SQL se escribe compatible con ambos para que funcione también en XAMPP. |
| Pruebas | pytest | Permite comprobar que la API funciona sin probar todo a mano. |

### Qué problemas del diagnóstico resuelve esta arquitectura

| Problema (sección 1) | Cómo se resuelve |
|---|---|
| 1. `create_app` repetido | Solo existirá en `frontend/src/__init__.py`. |
| 2, 3 y 4. Formularios que no envían y datos escritos a mano | Los formularios enviarán los datos a Flask, Flask a la API y la API los guardará en la base de datos; las listas se llenarán desde la base de datos. |
| 5. Sin base de datos ni API | Se agregan `backend/` y `database/`. |
| 6. Sin login ni roles | La API emite un token con el rol del usuario y revisa los permisos en cada ruta. |
| 7 y 8. Mezcla de idiomas y nombres que no coinciden | Todo en español y con nombres del negocio: `clients` pasa a contratistas y `products` a repuestos. |
| 18 y 19. Forma de ejecutar y `debug=True` fijo | El README explicará cómo ejecutar cada parte y la configuración vendrá del `.env`. |

## 6. Estructura de carpetas

Estructura prevista del proyecto. Las carpetas `frontend/`, `backend/` y `database/` todavía no existen: se crearán cuando empiece el desarrollo.

```
facturApp/
├── ARCHIVOS/              Documentos de referencia: guía, rúbrica y notas
├── _backup/               Copia del prototipo original, sin cambios
├── CLAUDE.md              Contexto y reglas del proyecto para la IA
├── README.md              Qué es el proyecto y cómo ejecutarlo
├── frontend/              Aplicación Flask (pantallas)
│   ├── src/
│   │   ├── __init__.py    create_app y registro de Blueprints (solo aquí)
│   │   ├── app.py         Punto de arranque del frontend
│   │   ├── controllers/   Un Blueprint por módulo: reciben la petición y muestran la pantalla
│   │   ├── services/      Cliente que llama a la API
│   │   ├── templates/     layout.html y una carpeta de plantillas por módulo
│   │   └── static/        CSS, JavaScript e imágenes
│   ├── .env.example       Variables del frontend sin valores reales
│   └── requirements.txt   Librerías del frontend
├── backend/               API FastAPI organizada en capas
│   ├── app/
│   │   ├── main.py        Punto de arranque de la API
│   │   ├── database.py    Conexión a MySQL o MariaDB con PyMySQL
│   │   ├── routers/       Capa de rutas: recibe la petición y responde en JSON
│   │   ├── schemas/       Capa de validación: forma de los datos con Pydantic
│   │   ├── services/      Capa de reglas del negocio: permisos, estados e historial
│   │   └── repositories/  Capa de datos: consultas SQL de cada módulo
│   ├── tests/             Pruebas con pytest
│   ├── .env.example       Variables del backend sin valores reales
│   └── requirements.txt   Librerías del backend
├── database/              Base de datos
│   ├── schema.sql         Creación de las tablas
│   └── seed.sql           Datos iniciales de prueba
└── entregables/           Documentos que se entregan
```

Las capas del backend se llaman en orden: **routers → services → repositories → base de datos**. Cada capa solo habla con la siguiente.
