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

**Total:** 30 historias, 19 de la fase 1 y 11 de la fase 2.

## 3. Historias de usuario

Los textos entre comillas son los **mensajes exactos** que verá el usuario en pantalla.

### Grupo: Acceso

#### HU-01. Iniciar sesión (Todos, fase 1)

**Como** usuario del sistema, **quiero** entrar con mi correo y mi contraseña, **para** usar las opciones de mi rol.

1. **Dado** que tengo un usuario activo, **cuando** escribo mi correo y mi contraseña correctos, **entonces** entro a la página de inicio de mi rol.
2. **Dado** que estoy en la pantalla de inicio de sesión, **cuando** escribo un correo que no existe o una contraseña incorrecta, **entonces** sigo en la misma pantalla y veo el mensaje "Correo o contraseña incorrectos.".
3. **Dado** que mi usuario fue desactivado por el Admin, **cuando** escribo mi correo y mi contraseña correctos, **entonces** no puedo entrar y veo el mensaje "Su usuario está desactivado. Comuníquese con el administrador.".
4. **Dado** que estoy en la pantalla de inicio de sesión, **cuando** dejo vacío el correo o la contraseña y presiono "Ingresar", **entonces** no se envía el formulario y veo el mensaje "Escriba su correo y su contraseña.".

#### HU-02. Cerrar sesión (Todos, fase 1)

**Como** usuario del sistema, **quiero** cerrar mi sesión, **para** que nadie más use el sistema con mi cuenta en este equipo.

1. **Dado** que inicié sesión, **cuando** presiono "Cerrar sesión", **entonces** vuelvo a la pantalla de inicio de sesión y veo el mensaje "Sesión cerrada.".
2. **Dado** que cerré sesión, **cuando** intento abrir una página interna (por ejemplo, con el botón "Atrás" del navegador), **entonces** el sistema me lleva a la pantalla de inicio de sesión.
3. **Dado** que dejé la sesión abierta sin usarla hasta que venció, **cuando** intento hacer cualquier acción, **entonces** vuelvo a la pantalla de inicio de sesión y veo el mensaje "Su sesión expiró. Inicie sesión de nuevo.".

#### HU-03. Ver solo las opciones de mi rol (Todos, fase 1)

**Como** usuario del sistema, **quiero** ver en el menú solo las opciones que me corresponden, **para** no confundirme con funciones que no puedo usar.

1. **Dado** que inicié sesión como Oficina radicadora, **cuando** veo el menú, **entonces** no aparecen Usuarios, Contratistas, Categorías, Repuestos ni Inventario.
2. **Dado** que inicié sesión como Oficina radicadora, **cuando** escribo en el navegador la dirección de una página del Admin, **entonces** vuelvo a mi página de inicio y veo el mensaje "No tiene permiso para ver esta página.".
3. **Dado** que inicié sesión como Admin, **cuando** veo el menú, **entonces** aparecen todas las opciones del sistema.

#### HU-04. Cambiar mi propia contraseña (Todos, fase 2)

**Como** usuario del sistema, **quiero** cambiar mi contraseña, **para** mantener mi cuenta segura.

1. **Dado** que inicié sesión, **cuando** escribo mi contraseña actual correcta y una contraseña nueva válida dos veces, **entonces** la contraseña cambia y veo el mensaje "Contraseña actualizada.".
2. **Dado** que estoy cambiando mi contraseña, **cuando** escribo mal mi contraseña actual, **entonces** la contraseña no cambia y veo el mensaje "La contraseña actual no es correcta.".
3. **Dado** que estoy cambiando mi contraseña, **cuando** la contraseña nueva y su confirmación no son iguales, **entonces** la contraseña no cambia y veo el mensaje "Las contraseñas nuevas no coinciden.".
4. **Dado** que estoy cambiando mi contraseña, **cuando** la contraseña nueva tiene menos de 8 caracteres, **entonces** la contraseña no cambia y veo el mensaje "La contraseña nueva debe tener al menos 8 caracteres.".

#### HU-05. Cambiar la contraseña temporal al entrar (Todos, fase 2)

**Como** usuario al que el Admin le restauró la contraseña, **quiero** que el sistema me pida cambiar la contraseña temporal al entrar, **para** que solo yo conozca mi contraseña.

1. **Dado** que el Admin me asignó una contraseña temporal, **cuando** inicio sesión con ella, **entonces** el sistema me lleva directo a la pantalla de cambio de contraseña y veo el mensaje "Debe cambiar su contraseña temporal antes de continuar.".
2. **Dado** que estoy en la pantalla de cambio de contraseña obligatorio, **cuando** intento abrir otra página del sistema, **entonces** vuelvo a la misma pantalla y sigo viendo el mensaje "Debe cambiar su contraseña temporal antes de continuar.".
3. **Dado** que estoy en la pantalla de cambio de contraseña obligatorio, **cuando** escribo como nueva la misma contraseña temporal, **entonces** la contraseña no cambia y veo el mensaje "La contraseña nueva debe ser diferente a la temporal.".
4. **Dado** que estoy en la pantalla de cambio de contraseña obligatorio, **cuando** guardo una contraseña nueva válida, **entonces** entro a la página de inicio de mi rol y veo el mensaje "Contraseña actualizada.".

#### HU-06. Cambiar a la vista de Oficina sin volver a iniciar sesión (Admin, fase 2)

**Como** Admin, **quiero** ver el sistema como lo ve la Oficina radicadora sin cerrar mi sesión, **para** revisar o explicar lo que ellos ven.

1. **Dado** que inicié sesión como Admin, **cuando** presiono "Ver como Oficina radicadora", **entonces** el menú muestra solo las opciones de ese rol y aparece arriba el aviso "Está viendo el sistema como Oficina radicadora.".
2. **Dado** que estoy en la vista de Oficina radicadora, **cuando** presiono "Volver a la vista de Admin", **entonces** recupero todas mis opciones sin escribir de nuevo mi contraseña.
3. **Dado** que inicié sesión como Oficina radicadora, **cuando** veo el menú, **entonces** no aparece la opción "Ver como Oficina radicadora".
