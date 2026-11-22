# CONTEXTO DEL PROYECTO: facturApp

## Qué es
Sistema web para registrar solicitudes de repuestos para reparar equipos de refrigeración (neveras) y hacer la trazabilidad de la entrega de los repuestos y del estado de la solicitud, hasta que el equipo queda reparado o se devuelve. Incluye la remisión de cada entrega y el inventario de repuestos.
Proyecto formativo SENA – ADSO. El prototipo original (basado en el ejemplo del instructor) está en `_backup/original/ADSO-25T4-FacturApp-main.zip` y es la base de la estructura.

## Stack (obligatorio)
- Frontend: Python 3.12 + Flask 3 (Blueprints y create_app), plantillas Jinja2, HTML5, CSS3 propio (sin Bootstrap) y JavaScript (ES modules). Flask es requisito académico.
- Backend: FastAPI + Uvicorn, Pydantic v2, PyMySQL con SQL directo (sin ORM, sin SQLAlchemy), PyJWT y bcrypt.
- Base de datos: MySQL 8 o MariaDB. En este equipo se usa el MySQL 8.0.17 de AppServ (`C:\AppServ\MySQL`, con phpMyAdmin); el proyecto debe funcionar también con la MariaDB de XAMPP, así que el SQL debe ser compatible con ambos. Apache no se usa: Flask y FastAPI (Uvicorn) tienen su propio servidor. El modelo se diseña en MySQL Workbench (no instalado en este equipo; mientras tanto, phpMyAdmin).
- Pruebas: pytest.
- Python instalado: 3.12.10.

## Arquitectura
Navegador -> Flask (frontend, puerto 5000) -> API FastAPI (JSON, puerto 8000) -> MySQL o MariaDB (puerto 3306).
- El navegador solo habla con Flask. Flask guarda el token en su sesión y llama a la API desde el servidor.
- Flask nunca accede a la base de datos. Solo FastAPI habla con la base de datos.
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
Un solo login para todos: el sistema muestra las opciones según el rol. La tabla completa de permisos (con la fase de cada acción) está en `entregables/01-propuesta.md`, sección 4.
- Admin:
  - Gestiona usuarios y catálogos (contratistas, categorías, repuestos).
  - Activa/desactiva usuarios (un usuario inactivo no puede entrar).
  - Restaura contraseñas con una contraseña temporal; el usuario debe cambiarla en su siguiente inicio de sesión (fase 2).
  - Puede cambiar a la vista de Oficina radicadora sin volver a iniciar sesión (fase 2).
  - Es el único que registra entregas (totales o parciales) y cambia la trazabilidad de la entrega de repuestos.
  - Es el único que registra entradas al almacén y consulta el inventario.
- Oficina radicadora:
  - Crea y consulta solicitudes de repuestos.
  - Marca el estado de la solicitud (equipo reparado / devuelto).
  - Consulta y registra equipos.
  - Ve e imprime remisiones.
  - NO registra entregas ni cambia su trazabilidad. NO consulta el inventario. NO gestiona usuarios ni catálogos.
- Todos: cambian su propia contraseña (fase 2).
- El contratista (técnico reparador) es un dato de la solicitud, no un usuario del sistema.

## Datos de cada solicitud
- Código del equipo (nevera).
- Contratista (técnico reparador).
- Repuestos solicitados (1 o más), elegidos de un catálogo (mínimo código y nombre), con cantidad.
- Fecha de entrega.
- Entregas totales o parciales: por cada repuesto se ve lo entregado y lo pendiente; cada entrega genera su remisión y descuenta el stock.
- Trazabilidad de la entrega de repuestos.
- Trazabilidad de la solicitud (equipo reparado / devuelto).

## Módulos
Lo marcado con (fase 2) se construye después del MVP.

| Módulo | Pantallas | Quién |
|---|---|---|
| Autenticación | Login, cerrar sesión; cambiar contraseña (fase 2) | Todos |
| Inicio | Página de inicio con las opciones del rol; resumen de solicitudes por estado y entregas pendientes (fase 2) | Todos |
| Usuarios | Lista, formulario, activar/desactivar; restaurar contraseña (fase 2) | Admin |
| Contratistas | Lista, formulario | Admin |
| Equipos (neveras) | Lista, formulario; detalle con historial (fase 2) | Admin y Oficina |
| Categorías de repuesto | Lista, formulario | Admin |
| Repuestos (catálogo) | Lista, formulario | Admin |
| Inventario | Stock disponible por repuesto y entradas al almacén | Admin |
| Solicitudes | Lista, formulario nuevo, detalle con línea de tiempo y cambios de estado; filtros de la lista (fase 2) | Admin y Oficina (según permisos) |
| Remisiones | Remisión de cada entrega (número consecutivo, fecha, contratista, equipo, repuestos y cantidades), para ver e imprimir | Admin y Oficina (la genera el Admin al registrar la entrega) |

Correspondencia con el ejemplo: clients -> contratistas, products -> repuestos, categories -> categorías de repuesto, users -> usuarios. Equipos, solicitudes, inventario y remisiones son nuevos.

## Convenciones
- Nombres, textos y comentarios en español sencillo.
- Comentarios para principiantes: cabecera en cada archivo, docstring en cada función, explicar el porqué y los conceptos nuevos la primera vez que aparecen.
- Nunca credenciales en el código: usar .env y un .env.example sin valores reales.
- MVP primero: la fase 1 completa y funcionando antes de empezar la fase 2.
- Git: al terminar cada entregable (`entregables/NN-*.md`) o cada tarea completada (código, SQL, documentación), hacer commit y push a `main` sin preguntar. Nunca subir `.env` ni secretos.

## Alcance (detalle en `entregables/01-propuesta.md`, sección 3)
- Fase 1 (MVP): login con roles; usuarios (crear, editar, activar/desactivar); contratistas; catálogo de categorías y repuestos; equipos; inventario básico con entradas; solicitudes; entregas totales o parciales; estado reparado/devuelto; historial de cambios; remisión por entrega impresa desde el navegador; schema.sql, seed.sql, .env.example, README y pruebas pytest de login, permisos y entregas.
- Fase 2 (mejoras): cambiar la propia contraseña y restaurar con contraseña temporal; cambio de vista del Admin; inicio con resumen; filtros y búsqueda; historial por equipo; historial de movimientos y alerta de stock mínimo; remisión en PDF; reportes con exportación; más pruebas.
- NO incluye: facturación (precios, costos, impuestos), acceso de contratistas, compras a proveedores, notificaciones, recuperar contraseña por correo, firma electrónica, varias bodegas, agenda de técnicos, integración con otros sistemas, app móvil ni publicación en internet.
- Regla: el stock en almacén baja al registrar cada entrega; al crear la solicitud las cantidades quedan apartadas (stock en almacén, apartado y disponible). Ver RN-13.
- Si no hay stock disponible suficiente, la solicitud se crea y lo que falta queda "En espera"; la mercancía nueva se aparta primero para las solicitudes en espera más antiguas (RN-33).
- Correcciones (HU-31 a HU-37, fase 1, todas solo Admin): retractar entregas y entradas (motivo obligatorio, nada se borra), devolución de repuestos no usados (también en solicitudes cerradas), editar o anular solicitudes sin entregas vigentes, reabrir solicitudes cerradas (las anuladas no se reabren), reasignar contratista si el original fue desactivado, reemplazar un repuesto desactivado que no tiene stock (lo apartado sí se entrega, RN-34).
- Usuarios: puede haber varios Admin; un Admin no puede desactivarse a sí mismo ni al último Admin activo (RN-32).
- Toda acción que guarda, cambia o desactiva datos pide confirmación (RNF-09).

## Reglas de negocio
- La fuente única de las reglas es `entregables/02-requisitos.md`, sección 4 (RN-01 a RN-24). Los criterios de aceptación las citan, por ejemplo (RN-10).
- Pendiente para el modelo de datos (sección 7 de la propuesta): la numeración de remisiones (RN-18) debe usar un contador propio, no el autoincremento, para que una entrega fallida no deje números saltados.

## Reglas de catálogos (resumen; detalle en RN-05 a RN-08)
- Los registros de catálogos no se eliminan, se desactivan: dejan de aparecer en solicitudes nuevas pero siguen en el historial, entregas y remisiones.
- No se puede desactivar una categoría con repuestos activos.
- Nombres repetidos: se comparan sin importar mayúsculas ni espacios al inicio o al final.
- Repuesto: código y nombre únicos; categoría; unidad de medida (unidad, metro, litro o kilogramo). El stock empieza en 0, no se escribe a mano y solo cambia con entradas al almacén y entregas.
- Cantidades: siempre mayores que cero; enteras si la unidad es "unidad"; hasta 2 decimales si es metro, litro o kilogramo.
- Contratista: el dato único es la cédula o NIT (sin importar puntos, guiones ni espacios); se aceptan homónimos.
- Mensajes al usuario en "usted" (confirmado).
- Identificadores escritos por el usuario sin caracteres raros (RN-25).

## Decisiones de requisitos no funcionales (detalle en `entregables/02-requisitos.md`, sección 5)
- La sesión vence a las 2 horas sin actividad.
- Fechas dd/mm/aaaa, horas en formato de 12 horas (a. m. y p. m.), hora de Colombia, decimales con coma.
- Una remisión de hasta 15 repuestos cabe en una hoja carta.
- Preguntas abiertas pendientes: `entregables/02-requisitos.md`, sección 6 (PA-01 a PA-34).

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
- Situación actual del cliente: las solicitudes se llevan en un Excel compartido.
- Entregable 00 (método con IA): en curso.
- Entregable 02 (requisitos): terminado (`entregables/02-requisitos.md`, etiqueta v0.2-requisitos). Quedan por escribir los grupos Gestión de usuarios (HU-07 a HU-11) y Equipos (HU-15 y HU-16), y siguen abiertas las preguntas de la sección 6.
- Entregable 03 (modelo de datos): terminado (`entregables/03-modelo-datos.md`): 14 tablas, diagrama entidad-relación, diccionario de datos y relaciones. Valores provisionales hasta responder PA-06, PA-11 y PA-27. 
- `database/schema.sql`: creado y probado en MySQL 8.0.17 de AppServ (14 tablas, 14 PK, 10 UNIQUE, 27 FK, 18 CHECK; se puede ejecutar varias veces). Falta probarlo en MariaDB (XAMPP). 
- `database/seed.sql`: creado y probado (3 usuarios con hash de ejemplo, 3 categorías, 6 repuestos, 3 contratistas, 3 equipos, 2 solicitudes, 2 entregas: REM-000001 completa y REM-000002 parcial). El stock cuadra con los movimientos. Las contraseñas reales se crearán desde el backend (Entregable 06). La base `facturapp` de AppServ tiene cargados estos datos.
- Diseño de la propuesta:
  - Etapa 1 (arquitectura y carpetas): aprobada.
  - Etapa 2 (módulos y pantallas): aprobada.
  - Alcance por fases y tabla de permisos: aprobados.
  - Etapa 3 (modelo de base de datos): pendiente; irá en la sección 7 de la propuesta.
  - Etapa 4 (estados de trazabilidad): pendiente; aún no tiene sección asignada en la propuesta.
- `entregables/01-propuesta.md`:
  - Escritas: 1 (Diagnóstico), 2 (Problema y objetivo), 3 (Alcance), 4 (Roles, permisos y módulos), 5 (Stack y arquitectura) y 6 (Estructura de carpetas).
  - Pendientes: 7 (Modelo de datos preliminar), 8 (Acceso, seguridad y UI/UX), 9 (Buenas prácticas) y 10 (Ruta de entregables).
- Aún no hay código.
