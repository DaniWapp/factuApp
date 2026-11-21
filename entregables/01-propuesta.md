# Propuesta del proyecto FacturApp

## 1. Diagnóstico

Se revisó el prototipo guardado en `_backup/original/ADSO-25T4-FacturApp-main.zip`: una aplicación Flask con Blueprints y plantillas Jinja2 que muestra pantallas de contratistas, repuestos, categorías y usuarios.

### Lo que existe y lo que falta

| Área | Lo que existe | Lo que falta |
|---|---|---|
| Estructura Flask | `create_app`, 5 Blueprints (home, clients, categories, products, users) y un `layout.html` común | Carpeta `static/`, archivo `requirements.txt` e instrucciones para ejecutar |
| Pantallas | Formulario y lista de contratistas, repuestos, categorías y usuarios | Pantallas de login, equipos, solicitudes, inventario y remisiones |
| Formularios | Campos visibles con estilos de Bootstrap | Envío de datos, validación y mensajes de éxito o error |
| Datos | Filas de ejemplo escritas a mano en las tablas | Base de datos (MariaDB) con `schema.sql` y `seed.sql` |
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

## 2. Arquitectura

### Cómo se conectan las partes

```
Navegador -> Flask (frontend, puerto 5000) -> API FastAPI (JSON, puerto 8000) -> MariaDB (puerto 3306)
```

1. **El navegador solo habla con Flask.** El usuario nunca ve ni llama directamente a la API.
2. **Flask muestra las pantallas.** Recibe los formularios, se los envía a la API y guarda en su sesión el token del usuario que inició sesión.
3. **FastAPI aplica las reglas del negocio.** Valida los datos, revisa los permisos de cada rol, cambia los estados y guarda el historial.
4. **Solo FastAPI habla con la base de datos.** Flask nunca se conecta a MariaDB.

Frontend y backend se trabajan **como si vivieran en servidores separados**: cada uno tiene su propio entorno virtual, su `requirements.txt`, su `.env` y su `.env.example`. El frontend solo conoce la dirección de la API, que lee de su `.env`.

### Stack y por qué

| Parte | Tecnología | Por qué |
|---|---|---|
| Frontend | Python 3.12, Flask 3 (Blueprints y `create_app`), Jinja2, HTML5, CSS3 propio, JavaScript (ES modules) | Flask es requisito académico y el prototipo ya usa Blueprints. El CSS propio permite el diseño sobrio definido para el proyecto. |
| Backend | FastAPI, Uvicorn, Pydantic v2 | Separa las reglas del negocio de las pantallas, valida los datos automáticamente y genera la documentación de la API en `/docs`. |
| Acceso a datos | PyMySQL con SQL directo | Se escriben las consultas a mano, lo que ayuda a aprender SQL y a ver exactamente qué se ejecuta. |
| Seguridad | PyJWT y bcrypt | El token (JWT) identifica al usuario en cada llamada a la API y bcrypt guarda las contraseñas cifradas. |
| Base de datos | MariaDB de XAMPP, modelo en MySQL Workbench | Ya está instalada en el equipo y es compatible con MySQL. |
| Pruebas | pytest | Permite comprobar que la API funciona sin probar todo a mano. |

### Estructura de carpetas

```
facturApp/
├── ARCHIVOS/        Documentos de referencia (guía, rúbrica, notas)
├── _backup/         Copia del prototipo original, sin cambios
├── frontend/        Aplicación Flask
│   └── src/
│       ├── __init__.py    create_app y registro de Blueprints (solo aquí)
│       ├── app.py
│       ├── controllers/   Un archivo por módulo
│       ├── services/      Cliente que llama a la API
│       ├── templates/     layout.html y una carpeta por módulo
│       └── static/        CSS, JavaScript e imágenes
├── backend/         API FastAPI
│   └── app/
│       ├── main.py
│       ├── database.py    Conexión a MariaDB con PyMySQL
│       ├── repositories/  Consultas SQL de cada módulo
│       ├── schemas/       Validación de datos con Pydantic
│       ├── routers/       Rutas de la API por módulo
│       └── services/      Reglas del negocio: estados e historial
├── database/        schema.sql y seed.sql
└── entregables/     Documentos que se entregan
```

### Qué problemas del diagnóstico resuelve esta arquitectura

| Problema (sección 1) | Cómo se resuelve |
|---|---|
| 1. `create_app` repetido | Solo existirá en `frontend/src/__init__.py`. |
| 2, 3 y 4. Formularios que no envían y datos escritos a mano | Los formularios enviarán los datos a Flask, Flask a la API y la API los guardará en MariaDB; las listas se llenarán desde la base de datos. |
| 5. Sin base de datos ni API | Se agregan `backend/` y `database/`. |
| 6. Sin login ni roles | La API emite un token con el rol del usuario y revisa los permisos en cada ruta. |
| 7 y 8. Mezcla de idiomas y nombres que no coinciden | Todo en español y con nombres del negocio: `clients` pasa a contratistas y `products` a repuestos. |
| 18 y 19. Forma de ejecutar y `debug=True` fijo | El README explicará cómo ejecutar cada parte y la configuración vendrá del `.env`. |
