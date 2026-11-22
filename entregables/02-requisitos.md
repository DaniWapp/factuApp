# Requisitos del sistema FacturApp

## 1. Cómo leer este documento

### Historias de usuario

Cada historia describe algo que una persona quiere hacer en el sistema y por qué, contado desde su punto de vista. Se escribe así:

> **Como** [rol], **quiero** [acción], **para** [beneficio].

Ejemplo: *Como Oficina radicadora, quiero crear una solicitud con el código de la nevera, el contratista y los repuestos que necesita, para dejar de registrarla en el Excel compartido.*

### Criterios de aceptación

Cada historia tiene uno o más criterios que dicen cuándo está terminada. Si todos se cumplen, la historia está bien hecha. Se escriben así:

> **Dado** [situación inicial], **cuando** [acción], **entonces** [resultado esperado].

Ejemplo: *Dado que una solicitud pide 4 válvulas y ya se entregaron 2, cuando el Admin registra una entrega de 2 válvulas más, entonces la solicitud muestra 0 pendientes, el stock baja en 2 y se genera una remisión nueva.*

### Roles

- **Admin:** gestiona usuarios, catálogos, inventario y entregas.
- **Oficina radicadora:** crea y consulta solicitudes, registra equipos y marca el equipo como reparado o devuelto.
- **Todos:** Admin y Oficina radicadora.

### Fases

- **Fase 1 (MVP):** lo mínimo para que el sistema funcione completo, desde la solicitud hasta la remisión. Se construye primero.
- **Fase 2 (mejoras):** funciones que facilitan el trabajo pero no son indispensables. Se construyen solo cuando la fase 1 está completa y funcionando.

El alcance de cada fase está en `01-propuesta.md`, sección 3.

### Confirmaciones

Toda acción que guarda, cambia o desactiva datos pide confirmación antes de ejecutarse (RNF-09). Para no repetirlo, los criterios de aceptación no lo mencionan en cada caso.

## 2. Resumen de historias

| ID | Grupo | Título corto | Rol | Fase |
|---|---|---|---|:---:|
| HU-01 | Acceso | Iniciar sesión | Todos | 1 |
| HU-02 | Acceso | Cerrar sesión | Todos | 1 |
| HU-03 | Acceso | Ver solo las opciones de mi rol | Todos | 1 |
| HU-04 | Acceso | Cambiar mi propia contraseña | Todos | 2 |
| HU-05 | Acceso | Cambiar la contraseña temporal al entrar | Todos | 2 |
| HU-06 | Acceso | Cambiar a la vista de Oficina sin volver a iniciar sesión | Admin | 2 |
| HU-07 | Gestión de usuarios | Crear usuario | Admin | 1 |
| HU-08 | Gestión de usuarios | Editar usuario | Admin | 1 |
| HU-09 | Gestión de usuarios | Listar usuarios | Admin | 1 |
| HU-10 | Gestión de usuarios | Activar o desactivar usuario | Admin | 1 |
| HU-11 | Gestión de usuarios | Restaurar contraseña con una temporal | Admin | 2 |
| HU-12 | Catálogos | Gestionar categorías de repuesto | Admin | 1 |
| HU-13 | Catálogos | Gestionar repuestos (código y nombre) | Admin | 1 |
| HU-14 | Catálogos | Gestionar contratistas | Admin | 1 |
| HU-15 | Catálogos | Registrar y listar equipos (neveras) | Todos | 1 |
| HU-16 | Catálogos | Ver historial de solicitudes de un equipo | Todos | 2 |
| HU-17 | Entregas | Crear solicitud de repuestos | Todos | 1 |
| HU-18 | Entregas | Listar solicitudes y ver detalle con línea de tiempo | Todos | 1 |
| HU-19 | Entregas | Registrar entrada de repuestos al almacén | Admin | 1 |
| HU-20 | Entregas | Consultar stock disponible | Admin | 1 |
| HU-21 | Entregas | Registrar entrega total o parcial | Admin | 1 |
| HU-22 | Entregas | Ver lo entregado y lo pendiente por repuesto | Todos | 1 |
| HU-23 | Entregas | Marcar equipo como reparado o devuelto | Todos | 1 |
| HU-24 | Entregas | Ver e imprimir remisión | Todos | 1 |
| HU-25 | Entregas | Filtrar y buscar solicitudes | Todos | 2 |
| HU-26 | Entregas | Ver resumen en la página de inicio | Todos | 2 |
| HU-27 | Entregas | Ver historial de movimientos del inventario | Admin | 2 |
| HU-28 | Entregas | Recibir alerta de stock mínimo | Admin | 2 |
| HU-29 | Entregas | Descargar remisión en PDF | Todos | 2 |
| HU-30 | Entregas | Generar y exportar reportes | Admin | 2 |
| HU-31 | Entregas | Retractar una entrega | Admin | 1 |
| HU-32 | Entregas | Corregir una entrada al almacén | Admin | 1 |
| HU-33 | Entregas | Registrar devolución de repuestos no usados | Admin | 1 |
| HU-34 | Entregas | Editar o anular una solicitud | Admin | 1 |
| HU-35 | Entregas | Reabrir una solicitud cerrada | Admin | 1 |
| HU-36 | Entregas | Reasignar el contratista de una solicitud | Admin | 1 |
| HU-37 | Entregas | Reemplazar un repuesto desactivado en una solicitud | Admin | 1 |

**Total:** 37 historias, 26 de la fase 1 y 11 de la fase 2.

## 3. Historias de usuario

Los textos entre comillas son los **mensajes exactos** que verá el usuario en pantalla.

### Grupo: Acceso

#### HU-01. Iniciar sesión (Todos, fase 1)

**Como** usuario del sistema, **quiero** entrar con mi correo y mi contraseña, **para** usar las opciones de mi rol.

1. **Dado** que tengo un usuario activo, **cuando** escribo mi correo y mi contraseña correctos, **entonces** entro a la página de inicio de mi rol. (RN-01)
2. **Dado** que estoy en la pantalla de inicio de sesión, **cuando** escribo un correo que no existe o una contraseña incorrecta, **entonces** sigo en la misma pantalla y veo el mensaje "Correo o contraseña incorrectos.".
3. **Dado** que mi usuario fue desactivado por el Admin, **cuando** escribo mi correo y mi contraseña correctos, **entonces** no puedo entrar y veo el mensaje "Su usuario está desactivado. Comuníquese con el administrador.". (RN-01)
4. **Dado** que estoy en la pantalla de inicio de sesión, **cuando** dejo vacío el correo o la contraseña y presiono "Ingresar", **entonces** no se envía el formulario y veo el mensaje "Escriba su correo y su contraseña.".

#### HU-02. Cerrar sesión (Todos, fase 1)

**Como** usuario del sistema, **quiero** cerrar mi sesión, **para** que nadie más use el sistema con mi cuenta en este equipo.

1. **Dado** que inicié sesión, **cuando** presiono "Cerrar sesión", **entonces** vuelvo a la pantalla de inicio de sesión y veo el mensaje "Sesión cerrada.".
2. **Dado** que cerré sesión, **cuando** intento abrir una página interna (por ejemplo, con el botón "Atrás" del navegador), **entonces** el sistema me lleva a la pantalla de inicio de sesión.
3. **Dado** que dejé la sesión abierta sin usarla hasta que venció, **cuando** intento hacer cualquier acción, **entonces** vuelvo a la pantalla de inicio de sesión y veo el mensaje "Su sesión expiró. Inicie sesión de nuevo.".

#### HU-03. Ver solo las opciones de mi rol (Todos, fase 1)

**Como** usuario del sistema, **quiero** ver en el menú solo las opciones que me corresponden, **para** no confundirme con funciones que no puedo usar.

1. **Dado** que inicié sesión como Oficina radicadora, **cuando** veo el menú, **entonces** no aparecen Usuarios, Contratistas, Categorías, Repuestos ni Inventario. (RN-02)
2. **Dado** que inicié sesión como Oficina radicadora, **cuando** escribo en el navegador la dirección de una página del Admin, **entonces** vuelvo a mi página de inicio y veo el mensaje "No tiene permiso para ver esta página.". (RN-02)
3. **Dado** que inicié sesión como Admin, **cuando** veo el menú, **entonces** aparecen todas las opciones del sistema. (RN-02)

#### HU-04. Cambiar mi propia contraseña (Todos, fase 2)

**Como** usuario del sistema, **quiero** cambiar mi contraseña, **para** mantener mi cuenta segura.

1. **Dado** que inicié sesión, **cuando** escribo mi contraseña actual correcta y una contraseña nueva válida dos veces, **entonces** la contraseña cambia y veo el mensaje "Contraseña actualizada.".
2. **Dado** que estoy cambiando mi contraseña, **cuando** escribo mal mi contraseña actual, **entonces** la contraseña no cambia y veo el mensaje "La contraseña actual no es correcta.".
3. **Dado** que estoy cambiando mi contraseña, **cuando** la contraseña nueva y su confirmación no son iguales, **entonces** la contraseña no cambia y veo el mensaje "Las contraseñas nuevas no coinciden.".
4. **Dado** que estoy cambiando mi contraseña, **cuando** la contraseña nueva tiene menos de 8 caracteres, **entonces** la contraseña no cambia y veo el mensaje "La contraseña nueva debe tener al menos 8 caracteres.". (RN-03)

#### HU-05. Cambiar la contraseña temporal al entrar (Todos, fase 2)

**Como** usuario al que el Admin le restauró la contraseña, **quiero** que el sistema me pida cambiar la contraseña temporal al entrar, **para** que solo yo conozca mi contraseña.

1. **Dado** que el Admin me asignó una contraseña temporal, **cuando** inicio sesión con ella, **entonces** el sistema me lleva directo a la pantalla de cambio de contraseña y veo el mensaje "Debe cambiar su contraseña temporal antes de continuar.". (RN-04)
2. **Dado** que estoy en la pantalla de cambio de contraseña obligatorio, **cuando** intento abrir otra página del sistema, **entonces** vuelvo a la misma pantalla y sigo viendo el mensaje "Debe cambiar su contraseña temporal antes de continuar.". (RN-04)
3. **Dado** que estoy en la pantalla de cambio de contraseña obligatorio, **cuando** escribo como nueva la misma contraseña temporal, **entonces** la contraseña no cambia y veo el mensaje "La contraseña nueva debe ser diferente a la temporal.". (RN-04)
4. **Dado** que estoy en la pantalla de cambio de contraseña obligatorio, **cuando** guardo una contraseña nueva válida, **entonces** entro a la página de inicio de mi rol y veo el mensaje "Contraseña actualizada.". (RN-03)

#### HU-06. Cambiar a la vista de Oficina sin volver a iniciar sesión (Admin, fase 2)

**Como** Admin, **quiero** ver el sistema como lo ve la Oficina radicadora sin cerrar mi sesión, **para** revisar o explicar lo que ellos ven.

1. **Dado** que inicié sesión como Admin, **cuando** presiono "Ver como Oficina radicadora", **entonces** el menú muestra solo las opciones de ese rol y aparece arriba el aviso "Está viendo el sistema como Oficina radicadora.".
2. **Dado** que estoy en la vista de Oficina radicadora, **cuando** presiono "Volver a la vista de Admin", **entonces** recupero todas mis opciones sin escribir de nuevo mi contraseña.
3. **Dado** que inicié sesión como Oficina radicadora, **cuando** veo el menú, **entonces** no aparece la opción "Ver como Oficina radicadora". (RN-02)

### Grupo: Catálogos

**Reglas de este grupo:** RN-05 a RN-08 y RN-25 (sección 4).

#### HU-12. Gestionar categorías de repuesto (Admin, fase 1)

**Como** Admin, **quiero** crear, editar y listar las categorías de repuesto, **para** organizar el catálogo de repuestos.

1. **Dado** que estoy en el formulario de categorías, **cuando** guardo un nombre nuevo, **entonces** la categoría aparece en la lista y veo el mensaje "Categoría guardada.".
2. **Dado** que ya existe la categoría "Válvulas", **cuando** intento crear o renombrar otra categoría como "válvulas", **entonces** no se guarda y veo el mensaje "Ya existe una categoría con ese nombre.". (RN-07)
3. **Dado** que estoy en el formulario de categorías, **cuando** dejo el nombre vacío y presiono "Guardar", **entonces** no se guarda y veo el mensaje "Escriba el nombre de la categoría.".
4. **Dado** que una categoría tiene repuestos activos, **cuando** intento desactivarla, **entonces** sigue activa y veo el mensaje "Esta categoría tiene repuestos activos. Cámbielos de categoría o desactívelos primero.". (RN-06)

#### HU-13. Gestionar repuestos (Admin, fase 1)

**Como** Admin, **quiero** crear, editar y listar los repuestos con su código, nombre, categoría y unidad de medida, **para** que las solicitudes usen siempre el mismo catálogo.

1. **Dado** que estoy en el formulario de repuestos, **cuando** guardo un código, un nombre, una categoría y una unidad de medida (unidad, metro, litro o kilogramo), **entonces** el repuesto aparece en la lista con stock 0 y veo el mensaje "Repuesto guardado.". El formulario no tiene campo de stock: el stock no se escribe a mano. (RN-09)
2. **Dado** que ya existe un repuesto con el código "VAL-001" o con el nombre "Válvula de expansión", **cuando** intento crear o editar otro repuesto con ese mismo código o nombre, **entonces** no se guarda y veo el mensaje "Ya existe un repuesto con ese código." o "Ya existe un repuesto con ese nombre.", según el caso. (RN-07)
3. **Dado** que el repuesto "Válvula de expansión" tiene stock 5 y llega mercancía, **cuando** el Admin registra una entrada al almacén de 10 unidades (HU-19), **entonces** el stock queda en 15 y veo el mensaje "Entrada registrada. Stock actual: 15.". (RN-09)
4. **Dado** que estoy registrando una entrada al almacén, **cuando** escribo una cantidad negativa o cero (por ejemplo, -3 o 0), **entonces** no se guarda, el stock no cambia y veo el mensaje "La cantidad debe ser mayor que cero.". (RN-11)
5. **Dado** que el repuesto se maneja en **unidades**, **cuando** registro una entrada con decimales (por ejemplo, 2,5), **entonces** no se guarda y veo el mensaje "Este repuesto se maneja en unidades enteras. Escriba una cantidad sin decimales.". Si el repuesto se maneja en metros, litros o kilogramos, se acepta la cantidad con hasta 2 decimales (por ejemplo, 2,5 metros de tubería). (RN-12)
6. **Dado** que un repuesto ya tiene entregas registradas, **cuando** presiono "Desactivar", **entonces** el repuesto queda inactivo, ya no aparece al crear solicitudes nuevas, sigue apareciendo en las entregas y remisiones anteriores, y veo el mensaje "Repuesto desactivado. No aparecerá en solicitudes nuevas.". (RN-05)

#### HU-14. Gestionar contratistas (Admin, fase 1)

**Como** Admin, **quiero** crear, editar y listar los contratistas, **para** elegirlos al crear una solicitud.

El dato único del contratista es su **cédula o NIT**. Se aceptan contratistas con el mismo nombre (homónimos) si su documento es diferente.

1. **Dado** que estoy en el formulario de contratistas, **cuando** guardo la cédula o NIT, el nombre y el teléfono, **entonces** el contratista aparece en la lista y veo el mensaje "Contratista guardado.".
2. **Dado** que ya existe un contratista con el NIT 900.123.456-7, **cuando** intento crear o editar otro contratista con ese mismo documento (sin importar puntos, guiones ni espacios), **entonces** no se guarda y veo el mensaje "Ya existe un contratista con ese documento.". Si el documento es diferente, se guarda aunque el nombre se repita. (RN-08)
3. **Dado** que estoy en el formulario de contratistas, **cuando** dejo vacío el documento o el nombre y presiono "Guardar", **entonces** no se guarda y veo el mensaje "Escriba la cédula o NIT y el nombre del contratista.".
4. **Dado** que un contratista ya recibió entregas, **cuando** presiono "Desactivar", **entonces** el contratista queda inactivo, ya no aparece al crear solicitudes nuevas, sigue apareciendo en las solicitudes y remisiones anteriores, y veo el mensaje "Contratista desactivado. No aparecerá en solicitudes nuevas.". (RN-05)

### Grupo: Entregas

**Reglas de este grupo:** RN-09 a RN-24, RN-26 a RN-31, RN-33 y RN-34 (sección 4).

**Conceptos de este grupo:**

- Una **solicitud** pide repuestos para un equipo y un contratista. Una **entrega** es cada vez que el Admin entrega repuestos de esa solicitud, toda la cantidad o una parte. Cada entrega genera **una remisión**.
- **Estados provisionales** (se confirmarán en la etapa de trazabilidad):
  - Entrega de la solicitud: "Pendiente", "Parcial" y "Completa".
  - Solicitud: "Abierta", "Reparado", "Devuelto" y "Anulada".
- **Stock de un repuesto:**
  - **En almacén:** lo que hay físicamente.
  - **Apartado:** lo que está reservado para solicitudes abiertas y falta por entregar.
  - **Disponible:** en almacén menos apartado; es lo que se puede apartar para solicitudes nuevas.
  - **En espera:** lo que una solicitud pidió pero no se pudo apartar por falta de stock; se aparta cuando llega mercancía.
- **Formato provisional de los números:** solicitudes "SOL-000001" y remisiones "REM-000001".

#### HU-17. Crear solicitud de repuestos (Todos, fase 1)

**Como** Oficina radicadora o Admin, **quiero** registrar una solicitud con el equipo, el contratista, la fecha de entrega y los repuestos que necesita, **para** dejar de llevarla en el Excel compartido.

1. **Dado** que estoy en el formulario de nueva solicitud, **cuando** selecciono el equipo y el contratista, escribo la fecha de entrega y agrego al menos un repuesto con su cantidad, **entonces** la solicitud se guarda en estado "Abierta" con entrega "Pendiente", el sistema le asigna el siguiente número (por ejemplo, SOL-000045), las cantidades pedidas quedan apartadas en el inventario y veo el mensaje "Solicitud SOL-000045 creada.". (RN-13)
2. **Dado** que estoy en el formulario de nueva solicitud, **cuando** dejo sin seleccionar el equipo o el contratista, **entonces** no se guarda y veo el mensaje "Seleccione el equipo y el contratista.". (RN-14)
3. **Dado** que estoy en el formulario de nueva solicitud, **cuando** intento guardar sin repuestos, **entonces** no se guarda y veo el mensaje "Agregue al menos un repuesto.". Si agrego el mismo repuesto dos veces, veo el mensaje "El repuesto VAL-001 ya está en la solicitud. Cambie la cantidad en la fila existente.". (RN-15)
4. **Dado** que estoy en el formulario de nueva solicitud, **cuando** escribo una fecha de entrega anterior a hoy, **entonces** no se guarda y veo el mensaje "La fecha de entrega no puede ser anterior a hoy.". (RN-14)
5. **Dado** que una solicitud pide 5 válvulas y solo hay 3 disponibles, **cuando** la guardo, **entonces** la solicitud se crea igual, se apartan 3, las otras 2 quedan "En espera" de mercancía y veo el mensaje "Solicitud SOL-000046 creada. VAL-001: 3 apartadas y 2 en espera de mercancía.". (RN-13, RN-33)

#### HU-18. Listar solicitudes y ver detalle con línea de tiempo (Todos, fase 1)

**Como** Oficina radicadora o Admin, **quiero** ver la lista de solicitudes y el detalle de cada una, **para** saber en qué va cada solicitud y quién hizo cada cambio.

1. **Dado** que hay solicitudes registradas, **cuando** abro "Solicitudes", **entonces** veo la lista con número, fecha, equipo, contratista, estado de la entrega y estado de la solicitud, de la más reciente a la más antigua.
2. **Dado** que abro el detalle de una solicitud, **cuando** se carga la página, **entonces** veo sus datos, sus repuestos, sus remisiones y una línea de tiempo con cada acción (creación, entregas y cambios de estado), con fecha, hora y usuario. (RN-20)
3. **Dado** que inicié sesión como Oficina radicadora, **cuando** abro el detalle de una solicitud, **entonces** no aparece el botón "Registrar entrega". (RN-02)
4. **Dado** que no hay solicitudes registradas, **cuando** abro "Solicitudes", **entonces** veo el mensaje "No hay solicitudes registradas.".

#### HU-19. Registrar entrada de repuestos al almacén (Admin, fase 1)

**Como** Admin, **quiero** registrar los repuestos que llegan al almacén, **para** que el stock disponible sea real.

1. **Dado** que llega mercancía, **cuando** selecciono el repuesto, escribo la cantidad y, si quiero, una observación, **entonces** el stock sube en esa cantidad, se guardan solos la fecha, la hora y mi usuario, y veo el mensaje "Entrada registrada. Stock actual: [stock].". (RN-09, RN-20)
2. **Dado** que estoy registrando una entrada, **cuando** la cantidad no cumple las reglas del repuesto, **entonces** no se guarda y veo el mensaje que corresponde según HU-13 (criterios 4 y 5). (RN-11, RN-12)
3. **Dado** que un repuesto está desactivado, **cuando** busco repuestos para registrar una entrada, **entonces** ese repuesto no aparece en la lista. (RN-05)
4. **Dado** que hay solicitudes con válvulas "En espera", **cuando** registro una entrada de válvulas, **entonces** el sistema aparta esa mercancía para las solicitudes en espera, de la más antigua a la más reciente, y lo que sobre queda disponible. (RN-33)

#### HU-20. Consultar stock disponible (Admin, fase 1)

**Como** Admin, **quiero** ver el stock disponible de cada repuesto, **para** saber qué puedo entregar.

1. **Dado** que hay repuestos activos, **cuando** abro "Inventario", **entonces** veo el código, el nombre, la categoría, la unidad de medida y, de cada repuesto, el stock en almacén, lo apartado, el stock disponible y lo que está en espera, con los números alineados a la derecha. (RN-13, RN-33)
2. **Dado** que un repuesto tiene stock 0, **cuando** abro "Inventario", **entonces** ese repuesto aparece marcado como "Sin stock".
3. **Dado** que inicié sesión como Oficina radicadora, **cuando** intento abrir "Inventario", **entonces** vuelvo a mi página de inicio y veo el mensaje "No tiene permiso para ver esta página.". (RN-02)

#### HU-21. Registrar entrega total o parcial (Admin, fase 1)

**Como** Admin, **quiero** registrar los repuestos que entrego de una solicitud, todos o solo una parte, **para** que el stock, lo pendiente y la remisión queden al día.

1. **Dado** que la solicitud SOL-000045 pide 4 válvulas y hay 10 en stock, **cuando** registro una entrega de las 4 válvulas, **entonces** el stock baja a 6, la solicitud muestra 4 entregadas y 0 pendientes, su entrega pasa a "Completa" y veo el mensaje "Entrega registrada. Remisión REM-000124 generada.". (RN-09, RN-18, RN-21)
2. **Dado** que la misma solicitud pide 4 válvulas, **cuando** registro una entrega de solo 2, **entonces** el stock baja en 2, la solicitud muestra 2 entregadas y 2 pendientes y su entrega pasa a "Parcial". Cuando después registro las 2 restantes, se genera otra remisión y la entrega pasa a "Completa". (RN-18, RN-21)
3. **Dado** que entrego varios repuestos a la vez y uno de ellos no tiene stock suficiente (por ejemplo, pido entregar 3 y hay 1), **cuando** presiono "Registrar entrega", **entonces** **no se guarda nada**: ningún stock cambia, no se genera remisión, y veo el mensaje "No hay stock suficiente de VAL-001 Válvula de expansión. Disponible: 1.". (RN-10, RN-17)
4. **Dado** que a un repuesto le quedan 2 pendientes, **cuando** intento entregar 5, **entonces** no se guarda nada y veo el mensaje "No puede entregar más de lo pendiente. Pendiente de VAL-001: 2.". (RN-16, RN-17)
5. **Dado** que la última remisión generada es REM-000123, **cuando** registro una entrega, **entonces** su remisión recibe el número REM-000124. Los números nunca se repiten ni se saltan, y no se reutilizan. (RN-18)
6. **Dado** que registro una entrega, **cuando** se guarda, **entonces** el sistema guarda solos la fecha, la hora y mi usuario; no puedo cambiarlos, y aparecen en la línea de tiempo y en la remisión. (RN-20)
7. **Dado** que estoy en el formulario de entrega, **cuando** no escribo cantidad en ningún repuesto, **entonces** no se guarda y veo el mensaje "Indique la cantidad a entregar de al menos un repuesto.". El contratista no se escribe en este formulario: se toma de la solicitud, donde es obligatorio (HU-17, criterio 2). (RN-15, RN-17)

#### HU-22. Ver lo entregado y lo pendiente por repuesto (Todos, fase 1)

**Como** Oficina radicadora o Admin, **quiero** ver por cada repuesto cuánto se pidió, cuánto se entregó y cuánto falta, **para** saber si la solicitud está completa.

1. **Dado** que abro el detalle de una solicitud, **cuando** veo la tabla de repuestos, **entonces** cada fila muestra la cantidad solicitada, entregada y pendiente, con su unidad de medida.
2. **Dado** que todos los repuestos de una solicitud tienen 0 pendientes, **cuando** veo el detalle, **entonces** la entrega aparece como "Completa". (RN-21)
3. **Dado** que una solicitud no tiene ninguna entrega, **cuando** veo el detalle, **entonces** la entrega aparece como "Pendiente" y lo pendiente es igual a lo solicitado. (RN-21)

#### HU-23. Marcar equipo como reparado o devuelto (Todos, fase 1)

**Como** Oficina radicadora o Admin, **quiero** marcar si el equipo quedó reparado o se devolvió, **para** cerrar la solicitud.

1. **Dado** que una solicitud está "Abierta", **cuando** presiono "Marcar como reparado", **entonces** la solicitud pasa a "Reparado", la acción queda en la línea de tiempo con fecha, hora y usuario, y veo el mensaje "Solicitud marcada como reparada.". (RN-20)
2. **Dado** que una solicitud está "Abierta", **cuando** presiono "Marcar como devuelto" sin escribir el motivo, **entonces** no cambia y veo el mensaje "Escriba el motivo de la devolución.". (RN-23)
3. **Dado** que una solicitud tiene repuestos pendientes, **cuando** intento marcarla como reparada o devuelta, **entonces** veo la advertencia "La solicitud tiene repuestos pendientes por entregar. ¿Desea cerrarla de todas formas?" y solo cambia si confirmo. Al cerrarla, lo pendiente deja de estar apartado. (RN-13)
4. **Dado** que una solicitud está en "Reparado", "Devuelto" o "Anulada", **cuando** intento registrar otra entrega o cambiar su estado, **entonces** no se permite y veo el mensaje "La solicitud está cerrada. No se pueden registrar más cambios.". Para corregirla, el Admin puede reabrirla (HU-35). (RN-22)

#### HU-24. Ver e imprimir remisión (Todos, fase 1)

**Como** Oficina radicadora o Admin, **quiero** ver e imprimir la remisión de cada entrega, **para** que el contratista firme lo que recibió.

1. **Dado** que una solicitud tiene entregas, **cuando** abro una de sus remisiones, **entonces** veo el número de remisión, la fecha y hora, el número de solicitud, el equipo, el contratista con su cédula o NIT, el usuario que entregó y la tabla de repuestos con código, nombre, unidad y cantidad entregada.
2. **Dado** que estoy viendo una remisión, **cuando** presiono "Imprimir", **entonces** se abre la ventana de impresión del navegador y la hoja sale en tamaño carta, sin el menú ni los botones del sistema.
3. **Dado** que imprimo una remisión, **cuando** reviso la hoja, **entonces** al final tiene espacio para la firma de quien recibe, con las líneas "Recibido por", "Cédula", "Firma" y "Fecha", y otro espacio para "Entregado por".
4. **Dado** que una remisión corresponde a una entrega parcial, **cuando** la abro, **entonces** solo muestra las cantidades de esa entrega. Una remisión generada no se puede editar ni eliminar; si su entrega se retracta, queda marcada como "Retractada" (HU-31). (RN-19)

#### HU-25. Filtrar y buscar solicitudes (Todos, fase 2)

**Como** Oficina radicadora o Admin, **quiero** filtrar y buscar solicitudes, **para** encontrar rápido la que necesito.

1. **Dado** que estoy en la lista de solicitudes, **cuando** filtro por estado, equipo, contratista o rango de fechas, **entonces** solo veo las solicitudes que cumplen todos los filtros elegidos.
2. **Dado** que estoy en la lista de solicitudes, **cuando** busco por número de solicitud o por código de equipo, **entonces** veo las solicitudes que coinciden.
3. **Dado** que ninguna solicitud cumple los filtros, **cuando** aplico la búsqueda, **entonces** veo el mensaje "No se encontraron solicitudes con esos filtros.".

#### HU-26. Ver resumen en la página de inicio (Todos, fase 2)

**Como** Oficina radicadora o Admin, **quiero** ver un resumen al entrar, **para** saber qué está pendiente sin buscarlo.

1. **Dado** que inicié sesión, **cuando** abro la página de inicio, **entonces** veo cuántas solicitudes hay en cada estado y cuántas tienen entregas pendientes o parciales.
2. **Dado** que inicié sesión como Admin, **cuando** abro la página de inicio, **entonces** también veo los repuestos con stock bajo (HU-28). La Oficina radicadora no ve datos de stock. (RN-02)

#### HU-27. Ver historial de movimientos del inventario (Admin, fase 2)

**Como** Admin, **quiero** ver todas las entradas y salidas de un repuesto, **para** explicar por qué el stock tiene el valor actual.

1. **Dado** que un repuesto tiene entradas y entregas, **cuando** abro su historial de movimientos, **entonces** veo cada movimiento con fecha y hora, tipo (entrada o entrega), cantidad, usuario, número de remisión si es una entrega, y el stock que quedó después. (RN-09)
2. **Dado** que un repuesto no tiene movimientos, **cuando** abro su historial, **entonces** veo el mensaje "Este repuesto no tiene movimientos.".

#### HU-28. Recibir alerta de stock mínimo (Admin, fase 2)

**Como** Admin, **quiero** definir un stock mínimo por repuesto y ver una alerta cuando se alcance, **para** pedir mercancía a tiempo.

1. **Dado** que un repuesto tiene stock mínimo 5, **cuando** su stock llega a 5 o menos, **entonces** aparece marcado como "Stock bajo" en el inventario y en el resumen de inicio.
2. **Dado** que estoy editando el stock mínimo, **cuando** escribo un número negativo, **entonces** no se guarda y veo el mensaje "El stock mínimo no puede ser negativo.". (RN-24)

#### HU-29. Descargar remisión en PDF (Todos, fase 2)

**Como** Oficina radicadora o Admin, **quiero** descargar la remisión en PDF, **para** guardarla o enviarla sin imprimirla.

1. **Dado** que estoy viendo una remisión, **cuando** presiono "Descargar PDF", **entonces** se descarga un archivo con el nombre del número de remisión (por ejemplo, REM-000124.pdf) y el mismo contenido de la versión impresa, incluido el espacio para la firma.

#### HU-30. Generar y exportar reportes (Admin, fase 2)

**Como** Admin, **quiero** ver reportes de entregas, **para** conocer qué contratistas reciben más repuestos y qué repuestos se usan más.

1. **Dado** que hay entregas registradas, **cuando** elijo un rango de fechas y el reporte "Entregas por contratista" o "Repuestos más usados", **entonces** veo el resultado ordenado de mayor a menor.
2. **Dado** que estoy viendo un reporte, **cuando** presiono "Exportar", **entonces** se descarga un archivo CSV que se puede abrir en Excel.
3. **Dado** que no hay entregas en el rango elegido, **cuando** genero el reporte, **entonces** veo el mensaje "No hay entregas en el rango de fechas elegido.".

#### HU-31. Retractar una entrega (Admin, fase 1)

**Como** Admin, **quiero** retractar una entrega que registré por error, **para** que el stock, lo pendiente y la remisión queden correctos.

1. **Dado** que la entrega con remisión REM-000124 registró 4 válvulas por error, **cuando** presiono "Retractar entrega", escribo el motivo y confirmo, **entonces** el stock en almacén sube en 4, esas 4 válvulas vuelven a quedar pendientes y apartadas, el estado de la entrega se recalcula y veo el mensaje "Entrega retractada. La remisión REM-000124 quedó marcada como retractada.". (RN-09, RN-13, RN-21, RN-26)
2. **Dado** que voy a retractar una entrega, **cuando** confirmo sin escribir el motivo, **entonces** no se retracta y veo el mensaje "Escriba el motivo de la retracción.". (RN-26)
3. **Dado** que una entrega fue retractada, **cuando** abro su remisión, **entonces** la veo con la marca "RETRACTADA", el motivo, la fecha, la hora y el usuario que la retractó; su número no se reutiliza y no se puede retractar de nuevo. (RN-18, RN-19, RN-20)
4. **Dado** que la solicitud está cerrada, **cuando** intento retractar una de sus entregas, **entonces** no se permite y veo el mensaje "La solicitud está cerrada. No se pueden registrar más cambios.". La Oficina radicadora no ve el botón "Retractar entrega". (RN-02, RN-22)

#### HU-32. Corregir una entrada al almacén (Admin, fase 1)

**Como** Admin, **quiero** retractar una entrada al almacén que registré por error, **para** que el stock vuelva a ser real.

1. **Dado** que registré por error una entrada de 10 válvulas (eran 1), **cuando** presiono "Retractar entrada", escribo el motivo y confirmo, **entonces** el stock en almacén baja en 10, la entrada queda marcada como "Retractada" en el historial y veo el mensaje "Entrada retractada. Stock actual: [stock].". Después registro la entrada correcta (HU-19). (RN-09, RN-26)
2. **Dado** que voy a retractar una entrada, **cuando** confirmo sin escribir el motivo, **entonces** no se retracta y veo el mensaje "Escriba el motivo de la retracción.". (RN-26)
3. **Dado** que parte de esa entrada ya se entregó o está apartada, **cuando** intento retractarla, **entonces** no se retracta y veo el mensaje "No se puede retractar la entrada: ese stock ya fue entregado o está apartado.". (RN-10, RN-27)

#### HU-33. Registrar devolución de repuestos no usados (Admin, fase 1)

**Como** Admin, **quiero** registrar los repuestos que el contratista devuelve sin usar, **para** que vuelvan al stock.

1. **Dado** que en la solicitud SOL-000045 se entregaron 4 válvulas y el contratista devuelve 1 sin usar, **cuando** registro la devolución de 1 válvula, **entonces** el stock en almacén sube en 1, la devolución queda en la línea de tiempo con fecha, hora y usuario, lo pendiente no cambia y veo el mensaje "Devolución registrada. Stock actual: [stock].". Se puede registrar aunque la solicitud esté cerrada. (RN-09, RN-20, RN-22)
2. **Dado** que de un repuesto se entregaron 4 y ya se devolvió 1, **cuando** intento devolver 5, **entonces** no se guarda y veo el mensaje "No puede devolver más de lo entregado. Entregado sin devolver de VAL-001: 3.". (RN-28)
3. **Dado** que estoy registrando una devolución, **cuando** la cantidad no cumple las reglas del repuesto, **entonces** no se guarda y veo el mensaje que corresponde según HU-13 (criterios 4 y 5). (RN-11, RN-12)

#### HU-34. Editar o anular una solicitud (Admin, fase 1)

**Como** Admin, **quiero** corregir o anular una solicitud que se creó por error, **para** que no quede información equivocada ni repuestos apartados sin razón.

1. **Dado** que una solicitud no tiene entregas vigentes, **cuando** cambio su equipo, contratista, fecha de entrega o repuestos y guardo, **entonces** lo apartado se ajusta, el cambio queda en la línea de tiempo y veo el mensaje "Solicitud SOL-000045 actualizada.". (RN-13, RN-20, RN-29)
2. **Dado** que una solicitud tiene entregas vigentes (sin retractar), **cuando** intento editarla o anularla, **entonces** no se permite y veo el mensaje "La solicitud ya tiene entregas. Retracte las entregas antes de editarla o anularla.". (RN-29)
3. **Dado** que una solicitud no tiene entregas vigentes, **cuando** presiono "Anular solicitud", escribo el motivo y confirmo, **entonces** pasa a "Anulada", lo apartado se libera y veo el mensaje "Solicitud SOL-000045 anulada.". (RN-13, RN-22, RN-29)
4. **Dado** que voy a anular una solicitud, **cuando** confirmo sin escribir el motivo, **entonces** no se anula y veo el mensaje "Escriba el motivo de la anulación.". La Oficina radicadora no ve los botones "Editar solicitud" ni "Anular solicitud". (RN-02, RN-29)

#### HU-35. Reabrir una solicitud cerrada (Admin, fase 1)

**Como** Admin, **quiero** reabrir una solicitud que se cerró por error, **para** poder seguir registrando entregas o corregirla.

1. **Dado** que una solicitud está en "Reparado" o "Devuelto", **cuando** presiono "Reabrir solicitud", escribo el motivo y confirmo, **entonces** vuelve a "Abierta", lo pendiente vuelve a quedar apartado, la acción queda en la línea de tiempo y veo el mensaje "Solicitud SOL-000045 reabierta.". (RN-13, RN-20, RN-30)
2. **Dado** que voy a reabrir una solicitud, **cuando** confirmo sin escribir el motivo, **entonces** no se reabre y veo el mensaje "Escriba el motivo para reabrir la solicitud.". (RN-30)
3. **Dado** que una solicitud está "Anulada", **cuando** abro su detalle, **entonces** no aparece el botón "Reabrir solicitud". (RN-30)
4. **Dado** que inicié sesión como Oficina radicadora, **cuando** abro una solicitud cerrada, **entonces** no aparece el botón "Reabrir solicitud". (RN-02, RN-30)

#### HU-36. Reasignar el contratista de una solicitud (Admin, fase 1)

**Como** Admin, **quiero** cambiar el contratista de una solicitud abierta, **para** terminar de entregar los repuestos pendientes cuando el contratista original fue desactivado.

1. **Dado** que la solicitud SOL-000045 tiene 2 válvulas pendientes y su contratista "Indufrial" fue desactivado, **cuando** intento registrar una entrega, **entonces** no se permite y veo el mensaje "El contratista de esta solicitud está desactivado. Reasigne un contratista activo antes de registrar la entrega.". (RN-31)
2. **Dado** que estoy en una solicitud abierta, **cuando** presiono "Reasignar contratista", elijo un contratista activo y confirmo, **entonces** la solicitud queda con el nuevo contratista, la línea de tiempo muestra el contratista anterior y el nuevo con fecha, hora y usuario, y veo el mensaje "Contratista reasignado.". (RN-20, RN-31)
3. **Dado** que una solicitud tuvo entregas con el contratista anterior, **cuando** se reasigna, **entonces** las remisiones anteriores conservan el contratista que recibió en su momento; solo las entregas nuevas salen con el nuevo contratista. (RN-19)
4. **Dado** que estoy reasignando el contratista, **cuando** busco en la lista, **entonces** solo aparecen contratistas activos. La Oficina radicadora no ve el botón "Reasignar contratista". (RN-02, RN-05)

#### HU-37. Reemplazar un repuesto desactivado en una solicitud (Admin, fase 1)

**Como** Admin, **quiero** cambiar por otro un repuesto desactivado que todavía falta por entregar y no tiene stock, **para** que la solicitud no quede esperando algo que nunca va a llegar.

1. **Dado** que la solicitud SOL-000045 tiene 2 válvulas VAL-001 pendientes apartadas y VAL-001 fue desactivado, **cuando** registro la entrega de esas 2 válvulas, **entonces** se entregan normalmente, porque sí existen en el almacén. (RN-34)
2. **Dado** que VAL-001 fue desactivado y la solicitud tiene 2 unidades en espera sin stock, **cuando** intento registrar la entrega, **entonces** esas 2 unidades no se pueden entregar y veo el mensaje "El repuesto VAL-001 está desactivado y no tiene stock. Reemplácelo por otro repuesto en la solicitud.". (RN-34)
3. **Dado** ese mismo caso, **cuando** presiono "Reemplazar repuesto", elijo un repuesto activo y confirmo, **entonces** las 2 unidades en espera de VAL-001 salen de la solicitud, el repuesto nuevo entra con esa cantidad (apartada o en espera, según el stock), la línea de tiempo muestra el repuesto anterior y el nuevo, y veo el mensaje "Repuesto reemplazado.". (RN-13, RN-20, RN-33, RN-34)
4. **Dado** que VAL-001 ya tenía entregas en la solicitud, **cuando** se reemplaza, **entonces** las entregas y remisiones anteriores de VAL-001 no cambian. La Oficina radicadora no ve el botón "Reemplazar repuesto". (RN-02, RN-19)

## 4. Reglas de negocio

Son las reglas que el sistema **siempre** debe cumplir, sin importar desde qué pantalla se haga la acción. La API las revisa aunque alguien intente saltarse la pantalla. Los criterios de aceptación que dependen de una regla la citan al final, por ejemplo (RN-10).

| ID | Regla | Fase |
|---|---|:---:|
| RN-01 | Solo un usuario activo puede iniciar sesión. | 1 |
| RN-02 | Cada acción solo la puede hacer un rol que tenga permiso (tabla de la sección 4 de `01-propuesta.md`), aunque se escriba la dirección a mano. | 1 |
| RN-03 | Una contraseña nueva debe tener al menos 8 caracteres. | 2 |
| RN-04 | Quien entra con una contraseña temporal no puede usar ninguna otra función hasta cambiarla, y la nueva debe ser diferente a la temporal. | 2 |
| RN-05 | Los registros de los catálogos no se eliminan, se desactivan: un registro inactivo no se puede elegir en operaciones nuevas, pero se conserva en las anteriores. | 1 |
| RN-06 | No se puede desactivar una categoría que tenga repuestos activos. | 1 |
| RN-07 | No se repiten el nombre de una categoría ni el código o el nombre de un repuesto, sin importar mayúsculas ni espacios al inicio o al final. | 1 |
| RN-08 | No se repite la cédula o NIT de un contratista, sin importar puntos, guiones ni espacios; el nombre sí puede repetirse. | 1 |
| RN-09 | El stock no se escribe a mano: solo cambia con entradas al almacén, entregas, devoluciones de repuestos no usados y retracciones de entregas o de entradas. | 1 |
| RN-10 | El stock de un repuesto nunca queda negativo. | 1 |
| RN-11 | Toda cantidad (en solicitudes, entradas y entregas) debe ser mayor que cero. | 1 |
| RN-12 | Las cantidades son enteras si el repuesto se maneja en unidades, y pueden tener hasta 2 decimales si se maneja en metros, litros o kilogramos. | 1 |
| RN-13 | Al crear una solicitud, las cantidades pedidas quedan apartadas (o en espera, según RN-33): siguen en el almacén, pero no están disponibles para otras solicitudes. Lo apartado se libera al entregar, al anular la solicitud o al cerrarla con pendientes, y vuelve a apartarse si una entrega se retracta o la solicitud se reabre. | 1 |
| RN-14 | Toda solicitud tiene equipo y contratista, y su fecha de entrega no puede ser anterior al día en que se crea. | 1 |
| RN-15 | Toda solicitud y toda entrega tienen al menos un repuesto con cantidad, y una solicitud no repite el mismo repuesto. | 1 |
| RN-16 | De cada repuesto no se puede entregar más de lo que falta por entregar en la solicitud. | 1 |
| RN-17 | Una entrega se guarda completa o no se guarda: si algo falla, no cambia el stock y no se genera remisión. | 1 |
| RN-18 | Cada entrega genera una sola remisión, con un número consecutivo que no se repite, no se salta y no se reutiliza. | 1 |
| RN-19 | Una remisión generada no se puede editar ni eliminar; si su entrega se retracta, queda marcada como "Retractada" y conserva su número. | 1 |
| RN-20 | La fecha, la hora y el usuario de cada acción los guarda el sistema solo y no se pueden editar. | 1 |
| RN-21 | El estado de la entrega lo calcula el sistema: "Pendiente" si no hay nada entregado, "Parcial" si falta algo y "Completa" si no falta nada. Las entregas retractadas no cuentan. | 1 |
| RN-22 | Una solicitud en "Reparado", "Devuelto" o "Anulada" está cerrada: no acepta entregas, retracciones ni cambios de estado. Solo acepta devoluciones de repuestos no usados, y el Admin puede reabrirla según RN-30. | 1 |
| RN-23 | Para marcar una solicitud como "Devuelto" es obligatorio escribir el motivo. | 1 |
| RN-24 | El stock mínimo de un repuesto no puede ser negativo. | 2 |
| RN-25 | Los identificadores que escribe el usuario no aceptan caracteres raros: los códigos de repuesto y de equipo solo llevan letras sin tildes, números y guiones; la cédula o NIT solo lleva números, puntos y guiones. Si no cumple, no se guarda y aparece el mensaje "El código solo puede tener letras sin tildes, números y guiones." o "La cédula o NIT solo puede tener números, puntos y guiones.". | 1 |
| RN-26 | Solo el Admin retracta entregas o entradas, siempre con un motivo escrito. Nada se borra: lo retractado queda en el historial con su motivo, fecha, hora y usuario. | 1 |
| RN-27 | Una entrada solo se puede retractar si el stock en almacén no queda negativo ni por debajo de lo apartado. | 1 |
| RN-28 | De un repuesto no se puede devolver más de lo entregado en la solicitud menos lo que ya se devolvió. | 1 |
| RN-29 | Una solicitud solo se puede editar o anular si no tiene entregas vigentes (sin retractar); para anularla es obligatorio escribir el motivo. | 1 |
| RN-30 | Solo el Admin puede reabrir una solicitud en "Reparado" o "Devuelto", con un motivo escrito; una solicitud "Anulada" no se reabre. | 1 |
| RN-31 | Una solicitud abierta cuyo contratista fue desactivado no acepta entregas hasta que el Admin le reasigne un contratista activo; las remisiones anteriores conservan el contratista original. | 1 |
| RN-32 | Un Admin no puede desactivarse a sí mismo, y nadie puede desactivar al último Admin activo. | 1 |
| RN-33 | Si no hay stock disponible suficiente, la solicitud se crea igual: se aparta lo que haya y el resto queda "En espera"; cuando entra mercancía, se aparta primero para las solicitudes en espera más antiguas. | 1 |
| RN-34 | De un repuesto desactivado se puede entregar lo que ya está apartado en el almacén; lo que falta y no tiene stock no se puede entregar y el Admin debe reemplazarlo por un repuesto activo. | 1 |

## 5. Requisitos no funcionales

Describen **cómo** debe ser el sistema, no qué hace. Cada uno se puede comprobar con un número o una condición concreta. Las medidas de rendimiento se toman en el equipo local de desarrollo.

| ID | Tipo | Requisito |
|---|---|---|
| RNF-01 | Seguridad | Las contraseñas se guardan cifradas con bcrypt: en la tabla de usuarios ninguna contraseña aparece en texto plano. |
| RNF-02 | Seguridad | Todas las rutas de la API, excepto el inicio de sesión, responden 401 si no reciben un token válido y 403 si el rol no tiene permiso. |
| RNF-03 | Seguridad | La sesión vence después de 2 horas sin actividad y el usuario debe iniciar sesión de nuevo. |
| RNF-04 | Seguridad | La cookie de sesión de Flask es `HttpOnly` y `SameSite=Lax`: el JavaScript de la página no puede leer el token. |
| RNF-05 | Seguridad | Todas las consultas SQL usan parámetros de PyMySQL (`%s`); ninguna consulta se arma pegando texto escrito por el usuario. |
| RNF-06 | Seguridad | El repositorio no contiene archivos `.env` ni credenciales: solo `.env.example` con nombres de variables y sin valores reales. |
| RNF-07 | Usabilidad | Toda acción de guardar muestra en la misma pantalla un mensaje de éxito o de error, con los textos definidos en las historias. |
| RNF-08 | Usabilidad | Cuando un formulario tiene un error, los datos que el usuario ya escribió no se borran. |
| RNF-09 | Usabilidad | Toda acción que guarda, cambia o desactiva datos pide confirmación ("Confirmar" / "Cancelar") antes de ejecutarse; si el usuario cancela, no cambia nada. No piden confirmación iniciar sesión, buscar, filtrar ni moverse entre pantallas. |
| RNF-10 | Usabilidad | Cualquier pantalla del sistema se abre con máximo 2 clics desde el menú. |
| RNF-11 | Accesibilidad | Todo campo de formulario tiene una etiqueta conectada (`<label for>` con su `id`) y toda tabla separa encabezado y datos (`<thead>` y `<tbody>`). |
| RNF-12 | Accesibilidad | El texto tiene un contraste mínimo de 4,5:1 con su fondo (nivel AA de WCAG 2.1). |
| RNF-13 | Accesibilidad | Todas las acciones se pueden hacer solo con el teclado (Tab, Enter, Esc), y el elemento con foco siempre se ve resaltado. |
| RNF-14 | Accesibilidad | Ningún estado se indica solo con color: siempre va acompañado de su texto (por ejemplo, "Parcial" o "Sin stock"). |
| RNF-15 | Compatibilidad | El sistema funciona en las dos últimas versiones de Chrome, Edge y Firefox. |
| RNF-16 | Compatibilidad | Las pantallas se pueden usar desde 360 px de ancho (celular) sin desplazamiento horizontal de la página; las tablas anchas se desplazan dentro de su propio recuadro. |
| RNF-17 | Compatibilidad | Una remisión de hasta 15 repuestos se imprime completa, con el espacio de firma, en una sola hoja tamaño carta. |
| RNF-18 | Compatibilidad | `schema.sql` y `seed.sql` se ejecutan sin errores tanto en MySQL 8 (AppServ) como en MariaDB (XAMPP): usan solo SQL compatible con ambos. |
| RNF-19 | Rendimiento | Los listados cargan en menos de 2 segundos con 1.000 registros. |
| RNF-20 | Rendimiento | Registrar una entrega de 10 repuestos responde en menos de 2 segundos. |
| RNF-21 | Rendimiento | Una remisión se abre en pantalla en menos de 2 segundos. |
| RNF-22 | Mantenibilidad | Cada archivo de código tiene un comentario de cabecera y cada función tiene un docstring en español sencillo que explica qué hace y por qué. |
| RNF-23 | Mantenibilidad | El backend respeta sus capas: ningún archivo de `routers/` contiene SQL; el SQL solo está en `repositories/`. |
| RNF-24 | Mantenibilidad | El comando `pytest` corre las pruebas de login, permisos y entregas, y termina sin fallos. |
| RNF-25 | Mantenibilidad | Cada `requirements.txt` fija la versión exacta de cada librería (por ejemplo, `fastapi==x.y.z`). |
| RNF-26 | Mantenibilidad | Los nombres de tablas, variables y funciones están en español, sin tildes ni ñ (por ejemplo, `contrasena`, `fecha_entrega`). |
| RNF-27 | Instalación | Una persona con MySQL 8 o MariaDB (AppServ o XAMPP) y Python 3.12 instala y ejecuta el sistema siguiendo solo el README, en menos de 30 minutos. |
| RNF-28 | Instalación | La base de datos se crea solo con `schema.sql` y `seed.sql`, importándolos desde phpMyAdmin o MySQL Workbench. |
| RNF-29 | Instalación | Frontend y backend se instalan cada uno en su propio entorno virtual con `pip install -r requirements.txt` y se inician con un solo comando cada uno. |
| RNF-30 | Instalación | `seed.sql` crea un usuario Admin inicial y datos de prueba; el README indica sus credenciales, que son solo para pruebas. |
| RNF-31 | Idioma | Toda la interfaz está en español: menús, botones, mensajes y errores que ve el usuario; las páginas declaran `lang="es"`. |
| RNF-32 | Idioma | Las fechas se muestran como dd/mm/aaaa, las horas en formato de 12 horas (a. m. y p. m.) en hora de Colombia (UTC-5), y los decimales con coma (2,5). |
| RNF-33 | Idioma | Los mensajes al usuario lo tratan de "usted" (por ejemplo, "Escriba su correo y su contraseña."). |

## 6. Preguntas abiertas

Decisiones y casos que faltan por confirmar. Al responder cada pregunta se actualizará la historia o regla de la que depende.

### Decisiones propuestas que faltan por confirmar

| ID | Pregunta | Depende de |
|---|---|---|
| PA-01 | ¿Los usuarios entran con su correo (y no con un nombre de usuario)? | HU-01 |
| PA-02 | ¿Está bien que el login muestre el mismo mensaje para un correo que no existe y para una contraseña incorrecta, para no revelar qué correos están registrados? | HU-01 |
| PA-03 | ¿La contraseña debe tener mínimo 8 caracteres? ¿Se exige algo más, como números o mayúsculas? | RN-03, HU-04 |
| PA-04 | ¿Las unidades de medida son solo unidad, metro, litro y kilogramo? ¿Falta alguna, como libra o galón? | RN-12, HU-13 |
| PA-05 | ¿Los nombres de los estados son correctos? Entrega: "Pendiente", "Parcial" y "Completa". Solicitud: "Abierta", "Reparado" y "Devuelto". | RN-21, RN-22, HU-21, HU-22, HU-23 |
| PA-06 | ¿Está bien el formato de los números: SOL-000001 para solicitudes y REM-000001 para remisiones? ¿La numeración empieza de nuevo cada año? | RN-18, HU-17, HU-21 |
| PA-07 | ¿La fecha de entrega de la solicitud es la fecha en que se espera entregar los repuestos, y por eso no puede ser anterior a hoy? | RN-14, HU-17 |
| PA-08 | ¿Es obligatorio escribir el motivo cuando un equipo se marca como devuelto? | RN-23, HU-23 |
| PA-09 | ¿Se puede cerrar una solicitud que todavía tiene repuestos pendientes, después de confirmar la advertencia? | HU-23 |
| PA-10 | Además de cédula o NIT, nombre y teléfono, ¿qué otros datos se guardan del contratista (ciudad, correo, dirección)? | HU-14 |
| PA-11 | Al registrar una entrada al almacén, ¿basta con el repuesto, la cantidad y una observación, o se debe guardar también el número de la factura o del documento del proveedor? | HU-19 |
| PA-12 | ¿"Caracteres raros" en los identificadores se refiere a los códigos de repuesto y de equipo y a la cédula o NIT, con los caracteres permitidos que dice RN-25? | RN-25 |
| PA-13 | ¿Apruebas los demás valores de la sección 5: máximo 2 clics, menos de 2 segundos, instalación en menos de 30 minutos y navegadores Chrome, Edge y Firefox? | RNF-10, RNF-15, RNF-19 a RNF-21, RNF-27 |

### Casos que todavía no están definidos

| ID | Pregunta | Depende de |
|---|---|---|
| PA-14 | Si el Admin se equivoca al registrar una entrega, ¿cómo se corrige, si la remisión no se puede editar ni anular? **Respondida:** el Admin retracta la entrega con un motivo obligatorio. | RN-26, HU-31 |
| PA-15 | Si el Admin se equivoca al registrar una entrada al almacén, ¿cómo se corrige el stock? **Respondida:** el Admin retracta la entrada con un motivo y registra la correcta. | RN-26, RN-27, HU-32 |
| PA-16 | Si el contratista devuelve repuestos que no usó, ¿vuelven al stock? ¿Cómo se registra? **Respondida:** se registra una devolución que sube el stock. | RN-28, HU-33 |
| PA-17 | ¿Se puede editar o anular una solicitud que se creó por error, antes de que tenga entregas? **Respondida:** sí, mientras no tenga entregas vigentes; anular exige motivo. | RN-29, HU-34 |
| PA-18 | ¿Quién puede editar o anular una solicitud: solo quien la creó, cualquier Oficina radicadora o solo el Admin? **Respondida:** solo el Admin. | RN-02, HU-34 |
| PA-19 | Si una solicitud se cerró por error, ¿se puede volver a abrir? ¿Quién puede hacerlo? **Respondida:** sí; se propuso que solo el Admin, con motivo (confirmar en PA-32). | RN-30, HU-35 |
| PA-20 | ¿Un mismo equipo puede tener dos solicitudes abiertas al mismo tiempo? | RN-14, HU-17 |
| PA-21 | Si el Admin desactiva un repuesto o un contratista (deja de usarse), pero una solicitud abierta todavía tiene repuestos pendientes con ese repuesto o ese contratista, ¿se pueden terminar de entregar o la solicitud queda bloqueada? **Respondida para el contratista:** el Admin le reasigna un contratista activo. El caso del repuesto sigue en PA-33. | RN-31, HU-36 |
| PA-22 | Al crear una solicitud, ¿se debe apartar el stock para que otra solicitud no lo use? **Respondida:** sí, se aparta. | RN-13, HU-17, HU-20 |
| PA-23 | ¿Qué pasa si la fecha de entrega ya pasó y la solicitud sigue pendiente: se marca como atrasada o se avisa a alguien? | RN-14, HU-18 |
| PA-24 | ¿Puede haber más de un Admin? ¿Puede un Admin desactivarse a sí mismo o desactivar al último Admin activo? **Respondida:** puede haber varios Admin; un Admin no puede desactivarse a sí mismo ni desactivar al último Admin activo. | RN-32, HU-10 |
| PA-25 | Si el Admin desactiva a un usuario que tiene la sesión abierta, ¿lo saca del sistema de inmediato o al vencer la sesión? **Respondida:** de inmediato; en su siguiente acción la API responde 401 `USUARIO_DESACTIVADO` y Flask cierra la sesión (`04-arquitectura-api.md`, sección 5.3). | RN-01, RNF-03, HU-10 |
| PA-26 | Cuando el Admin cambia a la vista de Oficina radicadora, ¿puede hacer acciones de Admin desde esa vista o queda limitado como la Oficina? | RN-02, HU-06 |
| PA-27 | ¿Qué datos se guardan de un equipo además del código (marca, modelo, serie, ubicación)? ¿La Oficina radicadora puede editarlos o solo registrarlos? | RN-25, HU-15 |
| PA-28 | La contraseña del Admin inicial que crea `seed.sql`, ¿debe cambiarse obligatoriamente? Hoy el cambio de contraseña es de la fase 2. | RNF-30, HU-04, HU-05 |
| PA-29 | Ahora que el stock se aparta al crear la solicitud: si no hay stock disponible suficiente, ¿se puede crear la solicitud igual (y queda esperando mercancía) o el sistema no la deja crear? **Respondida:** se crea y lo que falta queda "En espera". | RN-33, HU-17 |
| PA-30 | ¿Está bien que una devolución de repuestos no usados se pueda registrar aunque la solicitud ya esté cerrada? **Respondida:** sí. | RN-22, HU-33 |
| PA-31 | ¿Las funciones nuevas para corregir errores (HU-31 a HU-35) van en la fase 1? **Respondida:** sí. | HU-31 a HU-36 |
| PA-32 | ¿Está bien que solo el Admin pueda reabrir una solicitud cerrada, y que una solicitud anulada no se pueda reabrir? **Respondida:** sí. | RN-30, HU-35 |
| PA-33 | Si el Admin desactiva un repuesto que todavía está pendiente en una solicitud abierta, ¿se puede terminar de entregar, o hay que cambiarlo por otro repuesto en la solicitud? **Respondida:** lo que está en el almacén se entrega; lo que no tiene stock se reemplaza por otro repuesto. | RN-34, HU-37 |
| PA-34 | Cuando llega mercancía, ¿está bien que el sistema la aparte solo para las solicitudes en espera más antiguas, o el Admin debe elegir a qué solicitud se aparta? **Respondida:** automáticamente, de la más antigua a la más reciente. | RN-33, HU-19 |
| PA-35 | Al editar una solicitud sin entregas, si se quita un repuesto, ¿se borra su fila del detalle o se deja con cantidad reemplazada o anulada? La regla general es que nada se borra. **Respondida:** se borra la fila (solo es posible mientras la solicitud no tenga entregas vigentes); el cambio queda registrado en el historial de la solicitud. | RN-05, RN-29, HU-34 |
| PA-36 | Cuando el Admin crea un usuario y le escribe una contraseña inicial, ¿esa contraseña debe ser temporal (el usuario la cambia al entrar)? Hoy el cambio de contraseña es de la fase 2. **Respondida:** sí, es temporal (`debe_cambiar_contrasena = 1`). | RN-04, HU-07 |
| PA-37 | Como la contraseña inicial es temporal (PA-36), el usuario necesita cambiarla al entrar por primera vez. ¿Se pasan a la fase 1 el cambio obligatorio de contraseña (HU-05) y la ruta `PUT /api/auth/contrasena`? Si siguen en la fase 2, en la fase 1 la marca se guarda pero no se exige. | RN-04, HU-05, HU-07 |
