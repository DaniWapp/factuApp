# CONTEXTO DEL PROYECTO: facturApp

## Qué es
Sistema web para registrar solicitudes de repuestos para reparar equipos de refrigeración (neveras) y hacer la trazabilidad de la entrega de los repuestos y del estado de la solicitud, hasta que el equipo queda reparado o se devuelve. Incluye la remisión de cada entrega y el inventario de repuestos.
Proyecto formativo SENA – ADSO. El proyecto de ejemplo del instructor está en `ARCHIVOS/ADSO-25T4-FacturApp-main.zip` y es la base de la estructura.

## Stack (obligatorio)
- Frontend: Python 3.12 + Flask 3 (Blueprints y create_app), plantillas Jinja2, HTML5, CSS3 propio (sin Bootstrap) y JavaScript (ES modules). Flask es requisito académico.
- Backend: FastAPI + Uvicorn, Pydantic v2, PyMySQL con SQL directo (sin ORM, sin SQLAlchemy), PyJWT y bcrypt.
- Base de datos: MariaDB de XAMPP (compatible con MySQL). El modelo se diseña en MySQL Workbench.
- Pruebas: pytest.
- Python instalado: 3.12.10.

## Arquitectura
Navegador -> Flask (frontend, puerto 5000) -> API FastAPI (JSON, puerto 8000) -> MariaDB (puerto 3306).
- El navegador solo habla con Flask. Flask guarda el token en su sesión y llama a la API desde el servidor.
- Flask nunca accede a la base de datos. Solo FastAPI habla con MariaDB.
- Frontend y backend se tratan como si vivieran en servidores separados: cada uno tiene su propio entorno virtual, su `requirements.txt`, su `.env` y su `.env.example`. El frontend solo conoce la URL de la API desde su `.env`.

## Documentos de referencia
- Antes de cada tarea, revisa la carpeta ARCHIVOS/: ahí están la guía del SENA, la rúbrica y los documentos que debes tener en cuenta.

## Carpetas
```
facturApp/
├── ARCHIVOS/        (documentos de referencia para la IA; no se modifican)
├── frontend/        (aplicación Flask, mismo patrón del ejemplo)
│   └── src/
│       ├── __init__.py   (create_app + registro de Blueprints; solo aquí)
│       ├── app.py
│       ├── controllers/  (un archivo por módulo)
│       ├── services/     (cliente que llama a la API)
│       ├── templates/    (layout.html + una carpeta por módulo)
│       └── static/       (css, js, imágenes)
├── backend/         (API FastAPI)
│   └── app/
│       ├── main.py
│       ├── database.py   (conexión PyMySQL)
│       ├── repositories/ (consultas SQL por módulo)
│       ├── schemas/      (validación Pydantic)
│       ├── routers/      (endpoints por módulo)
│       └── services/     (reglas: cambios de estado, historial)
├── database/        (schema.sql y seed.sql)
└── entregables/
```

## Roles y permisos
- Admin:
  - Gestiona usuarios y catálogos (contratistas, categorías, repuestos).
  - Activa/desactiva usuarios y restaura contraseñas.
  - Puede cambiar a la vista de Oficina radicadora sin volver a iniciar sesión.
  - Es el único que cambia la trazabilidad de la entrega de repuestos.
- Oficina radicadora:
  - Crea y consulta solicitudes de repuestos.
  - Marca el estado de la solicitud (equipo reparado / devuelto).
  - Consulta y registra equipos.
  - NO cambia la trazabilidad de la entrega de repuestos. NO gestiona usuarios ni catálogos.
- Todos: cambian su propia contraseña.
- El contratista (técnico reparador) es un dato de la solicitud, no un usuario del sistema.

## Datos de cada solicitud
- Código del equipo (nevera).
- Contratista (técnico reparador).
- Repuestos solicitados (1 o más), elegidos de un catálogo (mínimo código y nombre), con cantidad.
- Fecha de entrega.
- Trazabilidad de la entrega de repuestos.
- Trazabilidad de la solicitud (equipo reparado / devuelto).

## Módulos
| Módulo | Pantallas | Quién |
|---|---|---|
| Autenticación | Login, cerrar sesión, cambiar contraseña | Todos |
| Inicio | Resumen de solicitudes por estado y entregas pendientes | Todos |
| Usuarios | Lista, formulario, activar/desactivar, restaurar contraseña | Admin |
| Contratistas | Lista, formulario | Admin |
| Equipos (neveras) | Lista, formulario, detalle con historial | Admin y Oficina |
| Categorías de repuesto | Lista, formulario | Admin |
| Repuestos (catálogo) | Lista, formulario | Admin |
| Inventario | Stock disponible por repuesto (detalle por definir) | Por definir |
| Solicitudes | Lista con filtros, formulario nuevo, detalle con línea de tiempo y cambios de estado | Admin y Oficina (según permisos) |
| Remisiones | Remisión de cada entrega (detalle por definir) | Por definir |

Correspondencia con el ejemplo: clients -> contratistas, products -> repuestos, categories -> categorías de repuesto, users -> usuarios. Equipos, solicitudes, inventario y remisiones son nuevos.

## Convenciones
- Nombres, textos y comentarios en español sencillo.
- Comentarios para principiantes: cabecera en cada archivo, docstring en cada función, explicar el porqué y los conceptos nuevos la primera vez que aparecen.
- Nunca credenciales en el código: usar .env y un .env.example sin valores reales.
- MVP primero: la fase 1 completa y funcionando antes de empezar la fase 2 (fases por definir).

## Dirección visual (sistema y diapositivas)
Objetivo: un diseño sobrio, elegante y profesional, propio del mundo de facturApp (almacén y mantenimiento de refrigeración industrial), que NO parezca hecho por una IA.
Inspiración: fichas técnicas, placas de datos de equipos, remisiones y formatos de almacén. Orden, precisión y números bien alineados.

Hacer:
- Paleta sobria: neutros fríos (grises con un toque de azul) y UN solo color de acento, usado con moderación (acción principal, foco, elemento activo). Verde, ámbar y rojo solo para estados.
- Tipografía con carácter técnico: una familia para los textos (IBM Plex Sans o Source Sans 3) y una monoespaciada para códigos, números de remisión y cantidades (IBM Plex Mono), con una fuente del sistema como respaldo.
- Jerarquía por tamaño, peso y espacio, no por cajas de colores.
- Contenido alineado a la izquierda, sobre una cuadrícula; espacios consistentes en múltiplos de 4 px.
- Separar con espacio y líneas finas antes que con tarjetas. Bordes rectos o casi rectos (2 a 6 px). Sombras solo en lo que flota (menús y diálogos).
- Números con cifras tabulares, alineados a la derecha en las tablas.
- Íconos de línea simples, de una sola familia, y solo cuando ayudan a entender.
- Textos cortos, con el vocabulario del almacén: "Remisión", "Stock disponible", "Contratista".

Evitar (se ve "hecho por IA"):
- Degradados morado-azul o fondos con degradados de colores.
- Emojis como íconos o como decoración.
- Todo centrado; portadas gigantes con frases motivacionales.
- Todas las secciones dentro de tarjetas iguales, muy redondeadas y con sombra.
- Fondo crema con títulos en serif y acento terracota; fondo negro con un solo color neón.
- Efecto vidrio (glassmorphism), brillos, ilustraciones 3D e imágenes genéricas de stock.
- Numeraciones decorativas (01, 02, 03) cuando el orden no importa.
- Frases de relleno ("Potencia tu gestión", "Solución innovadora").

Diapositivas:
- Misma paleta y tipografías del sistema; nada de plantillas coloridas ni sugerencias automáticas de diseño.
- Una idea por diapositiva, con un título que diga la conclusión (no "Arquitectura", sino "El navegador solo habla con Flask").
- Máximo 3 líneas de texto, alineado a la izquierda, con mucho espacio libre.
- Capturas reales del sistema y diagramas propios en lugar de íconos o fotos de stock.

## Estado actual
- Entregable 00 (método con IA): en curso.
- Diseño de la propuesta:
  - Etapa 1 (arquitectura y carpetas): aprobada.
  - Etapa 2 (módulos y pantallas): aprobada.
  - Etapa 3 (modelo de base de datos): pendiente.
  - Etapa 4 (estados de trazabilidad): pendiente.
- Aún no hay código.
