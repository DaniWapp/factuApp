-- =====================================================================
-- Archivo:  database/schema.sql
-- Proyecto: FacturApp - Solicitud y entrega de repuestos de refrigeración
--
-- Qué hace:
--   Crea la base de datos "facturapp" y todas sus tablas, tal como se
--   aprobaron en entregables/03-modelo-datos.md.
--
-- Dónde funciona:
--   - MySQL 8 (por ejemplo, el de AppServ).
--   - MariaDB 10.4 o superior (por ejemplo, el de XAMPP).
--   Por eso se usa la colación utf8mb4_unicode_ci, que existe en los dos,
--   y no se usan funciones exclusivas de ninguno.
--
-- Cómo se ejecuta:
--   - Desde phpMyAdmin: pestaña "Importar" y elegir este archivo.
--   - Desde CMD o Git Bash (en la carpeta del proyecto):
--       mysql -u root -p --default-character-set=utf8mb4 < database/schema.sql
--   - Desde PowerShell (no acepta el símbolo <):
--       cmd /c "mysql -u root -p --default-character-set=utf8mb4 < database\schema.sql"
--   La opción --default-character-set=utf8mb4 evita que las tildes y la ñ
--   se guarden dañadas.
--
-- Conceptos que aparecen en este archivo:
--   - PRIMARY KEY (PK): identifica cada fila; no se repite.
--   - FOREIGN KEY (FK): obliga a que un valor exista en otra tabla.
--     Con ON DELETE RESTRICT no se puede borrar una fila que otra usa.
--   - UNIQUE: el valor no se puede repetir en la tabla.
--   - CHECK: condición que cada fila debe cumplir; si no se cumple,
--     la base de datos rechaza el INSERT o el UPDATE.
--   - ENGINE=InnoDB: motor que permite transacciones y llaves foráneas.
--
-- Las referencias RN-xx son reglas de negocio de entregables/02-requisitos.md.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. Base de datos
-- ---------------------------------------------------------------------

-- Crea la base de datos solo si todavía no existe.
-- utf8mb4 guarda cualquier carácter (tildes, ñ, símbolos).
-- utf8mb4_unicode_ci compara sin distinguir mayúsculas ni tildes:
-- "Válvulas" y "valvulas" se consideran iguales (RN-07).
CREATE DATABASE IF NOT EXISTS facturapp
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Indica que todo lo que sigue se hace dentro de "facturapp".
USE facturapp;


-- ---------------------------------------------------------------------
-- 2. Borrar las tablas anteriores
-- ---------------------------------------------------------------------

-- ¡ATENCIÓN! Estas líneas BORRAN las tablas y TODOS SUS DATOS.
-- Sirven para poder ejecutar este archivo varias veces y empezar de cero.
-- No ejecute este archivo en una base de datos con información real
-- sin antes hacer una copia de seguridad.
--
-- Se borran en orden inverso al de creación: primero las tablas que
-- dependen de otras y al final las tablas base. Así ninguna llave
-- foránea impide el borrado.
DROP TABLE IF EXISTS historial_solicitud;
DROP TABLE IF EXISTS movimientos_inventario;
DROP TABLE IF EXISTS devoluciones;
DROP TABLE IF EXISTS entradas_almacen;
DROP TABLE IF EXISTS detalle_entrega;
DROP TABLE IF EXISTS entregas;
DROP TABLE IF EXISTS detalle_solicitud;
DROP TABLE IF EXISTS solicitudes;
DROP TABLE IF EXISTS equipos;
DROP TABLE IF EXISTS contratistas;
DROP TABLE IF EXISTS repuestos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS consecutivos;


-- ---------------------------------------------------------------------
-- 3. Tablas base (no dependen de otras tablas)
-- ---------------------------------------------------------------------

-- Tabla usuarios: las personas que entran al sistema.
-- Guarda su rol, si están activas y si deben cambiar la contraseña.
CREATE TABLE usuarios (
    id                      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre                  VARCHAR(100) NOT NULL,
    correo                  VARCHAR(150) NOT NULL,
    -- La contraseña nunca se guarda en texto plano: solo su hash de bcrypt (RNF-01).
    contrasena_hash         VARCHAR(255) NOT NULL,
    -- 'admin' = Admin; 'oficina' = Oficina radicadora.
    rol                     ENUM('admin', 'oficina') NOT NULL,
    -- 1 = puede entrar; 0 = desactivado (RN-01).
    activo                  TINYINT(1) NOT NULL DEFAULT 1,
    -- 1 = tiene contraseña temporal y debe cambiarla al entrar (RN-04).
    debe_cambiar_contrasena TINYINT(1) NOT NULL DEFAULT 0,
    creado_en               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Llave primaria: identifica a cada usuario.
    CONSTRAINT pk_usuarios PRIMARY KEY (id),
    -- Dos usuarios no pueden tener el mismo correo, porque es con lo que entran.
    CONSTRAINT uq_usuarios_correo UNIQUE (correo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Tabla categorias: agrupa los repuestos (por ejemplo, "Válvulas").
CREATE TABLE categorias (
    id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre  VARCHAR(80) NOT NULL,
    -- 1 = activa; 0 = desactivada. Las categorías no se borran (RN-05).
    activo  TINYINT(1) NOT NULL DEFAULT 1,

    -- Llave primaria: identifica a cada categoría.
    CONSTRAINT pk_categorias PRIMARY KEY (id),
    -- El nombre no se repite, sin importar mayúsculas ni tildes (RN-07).
    CONSTRAINT uq_categorias_nombre UNIQUE (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Tabla contratistas: técnicos o empresas que reciben los repuestos.
CREATE TABLE contratistas (
    id                    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    -- Cédula o NIT tal como se escribió, por ejemplo 900.123.456-7.
    documento             VARCHAR(20) NOT NULL,
    -- El mismo documento solo con dígitos, por ejemplo 9001234567.
    -- La API lo calcula al guardar; sirve para detectar repetidos (RN-08).
    documento_normalizado VARCHAR(20) NOT NULL,
    -- El nombre sí puede repetirse (se aceptan homónimos).
    nombre                VARCHAR(120) NOT NULL,
    telefono              VARCHAR(20) NULL,
    -- 1 = activo; 0 = desactivado (RN-05, RN-31).
    activo                TINYINT(1) NOT NULL DEFAULT 1,

    -- Llave primaria: identifica a cada contratista.
    CONSTRAINT pk_contratistas PRIMARY KEY (id),
    -- Dos contratistas no pueden tener la misma cédula o NIT (RN-08).
    CONSTRAINT uq_contratistas_documento UNIQUE (documento_normalizado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Tabla consecutivos: guarda el último número usado de solicitudes (SOL)
-- y de remisiones (REM). La API lo bloquea con SELECT ... FOR UPDATE dentro
-- de una transacción para que un número no se repita ni se salte (RN-18).
CREATE TABLE consecutivos (
    -- 'SOL' para solicitudes y 'REM' para remisiones.
    tipo          VARCHAR(10) NOT NULL,
    ultimo_numero INT UNSIGNED NOT NULL DEFAULT 0,

    -- Llave primaria: un solo contador por tipo.
    CONSTRAINT pk_consecutivos PRIMARY KEY (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 4. Catálogos que dependen de las tablas base
-- ---------------------------------------------------------------------

-- Tabla repuestos: el catálogo de repuestos con su stock.
-- El stock disponible no se guarda: se calcula como
-- stock_almacen - stock_apartado.
CREATE TABLE repuestos (
    id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
    -- Código, por ejemplo VAL-001. La API valida los caracteres (RN-25).
    codigo         VARCHAR(30) NOT NULL,
    nombre         VARCHAR(120) NOT NULL,
    categoria_id   INT UNSIGNED NOT NULL,
    -- Cómo se cuenta el repuesto (RN-12).
    unidad_medida  ENUM('unidad', 'metro', 'litro', 'kilogramo') NOT NULL,
    -- Lo que hay físicamente en el almacén.
    stock_almacen  DECIMAL(12,2) NOT NULL DEFAULT 0,
    -- Lo reservado para solicitudes abiertas (RN-13).
    stock_apartado DECIMAL(12,2) NOT NULL DEFAULT 0,
    -- Nivel para la alerta de stock bajo (fase 2). Puede quedar vacío.
    stock_minimo   DECIMAL(12,2) NULL,
    -- 1 = activo; 0 = desactivado (RN-05, RN-34).
    activo         TINYINT(1) NOT NULL DEFAULT 1,

    -- Llave primaria: identifica a cada repuesto.
    CONSTRAINT pk_repuestos PRIMARY KEY (id),
    -- El código no se repite (RN-07).
    CONSTRAINT uq_repuestos_codigo UNIQUE (codigo),
    -- El nombre no se repite (RN-07).
    CONSTRAINT uq_repuestos_nombre UNIQUE (nombre),
    -- Cada repuesto pertenece a una categoría que debe existir.
    -- No se puede borrar una categoría que tenga repuestos.
    CONSTRAINT fk_repuestos_categoria FOREIGN KEY (categoria_id)
        REFERENCES categorias (id) ON DELETE RESTRICT,
    -- El stock en almacén nunca puede ser negativo (RN-10).
    CONSTRAINT ck_repuestos_stock_almacen CHECK (stock_almacen >= 0),
    -- Lo apartado no puede ser negativo ni mayor que lo que hay en el almacén (RN-27).
    CONSTRAINT ck_repuestos_stock_apartado CHECK (stock_apartado >= 0 AND stock_apartado <= stock_almacen),
    -- El stock mínimo, si se escribe, no puede ser negativo (RN-24).
    CONSTRAINT ck_repuestos_stock_minimo CHECK (stock_minimo IS NULL OR stock_minimo >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Tabla equipos: las neveras que se reparan.
-- Es provisional hasta definir qué otros datos se guardan (PA-27).
CREATE TABLE equipos (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    -- Código de la nevera. La API valida los caracteres (RN-25).
    codigo      VARCHAR(30) NOT NULL,
    -- Marca, modelo o ubicación, mientras se define PA-27.
    descripcion VARCHAR(150) NULL,
    -- 1 = activo; 0 = desactivado (RN-05).
    activo      TINYINT(1) NOT NULL DEFAULT 1,
    creado_por  INT UNSIGNED NOT NULL,
    creado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Llave primaria: identifica a cada equipo.
    CONSTRAINT pk_equipos PRIMARY KEY (id),
    -- El código de la nevera no se repite.
    CONSTRAINT uq_equipos_codigo UNIQUE (codigo),
    -- Quien registró el equipo debe ser un usuario existente.
    CONSTRAINT fk_equipos_creado_por FOREIGN KEY (creado_por)
        REFERENCES usuarios (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 5. Solicitudes y su detalle
-- ---------------------------------------------------------------------

-- Tabla solicitudes: cada solicitud de repuestos para reparar un equipo.
-- El estado de la entrega (pendiente, parcial, completa) no se guarda:
-- se calcula con detalle_solicitud (RN-21).
CREATE TABLE solicitudes (
    id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
    -- Número visible, por ejemplo SOL-000045 (RN-18).
    numero         VARCHAR(12) NOT NULL,
    equipo_id      INT UNSIGNED NOT NULL,
    -- Contratista actual; puede reasignarse (RN-31).
    contratista_id INT UNSIGNED NOT NULL,
    -- Fecha en que se espera entregar los repuestos (RN-14).
    fecha_entrega  DATE NOT NULL,
    estado         ENUM('abierta', 'reparado', 'devuelto', 'anulada') NOT NULL DEFAULT 'abierta',
    -- Motivo de la devolución o de la anulación.
    motivo_cierre  VARCHAR(255) NULL,
    creado_por     INT UNSIGNED NOT NULL,
    creado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Llave primaria: identifica a cada solicitud.
    CONSTRAINT pk_solicitudes PRIMARY KEY (id),
    -- El número de solicitud no se repite (RN-18).
    CONSTRAINT uq_solicitudes_numero UNIQUE (numero),
    -- La solicitud es para un equipo que debe existir (RN-14).
    CONSTRAINT fk_solicitudes_equipo FOREIGN KEY (equipo_id)
        REFERENCES equipos (id) ON DELETE RESTRICT,
    -- La solicitud tiene un contratista que debe existir (RN-14).
    CONSTRAINT fk_solicitudes_contratista FOREIGN KEY (contratista_id)
        REFERENCES contratistas (id) ON DELETE RESTRICT,
    -- Quien creó la solicitud debe ser un usuario existente (RN-20).
    CONSTRAINT fk_solicitudes_creado_por FOREIGN KEY (creado_por)
        REFERENCES usuarios (id) ON DELETE RESTRICT,
    -- Si la solicitud se marca como devuelta o anulada, el motivo es obligatorio (RN-23, RN-29).
    CONSTRAINT ck_solicitudes_motivo_cierre CHECK (
        estado NOT IN ('devuelto', 'anulada')
        OR (motivo_cierre IS NOT NULL AND TRIM(motivo_cierre) <> '')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índice para que los listados filtren rápido por estado (RNF-19).
CREATE INDEX ix_solicitudes_estado ON solicitudes (estado);


-- Tabla detalle_solicitud: los repuestos de cada solicitud.
-- Lo que está en espera no se guarda: se calcula como
-- cantidad_solicitada - cantidad_entregada - cantidad_apartada (RN-33).
CREATE TABLE detalle_solicitud (
    id                  INT UNSIGNED NOT NULL AUTO_INCREMENT,
    solicitud_id        INT UNSIGNED NOT NULL,
    repuesto_id         INT UNSIGNED NOT NULL,
    cantidad_solicitada DECIMAL(12,2) NOT NULL,
    -- Cantidad reservada en este momento (RN-13).
    cantidad_apartada   DECIMAL(12,2) NOT NULL DEFAULT 0,
    -- Suma de las entregas vigentes; la API la actualiza en la misma transacción.
    cantidad_entregada  DECIMAL(12,2) NOT NULL DEFAULT 0,
    -- Cantidad devuelta sin usar (RN-28).
    cantidad_devuelta   DECIMAL(12,2) NOT NULL DEFAULT 0,
    -- Fila del repuesto que reemplazó a este, si fue reemplazado (RN-34).
    reemplazado_por_id  INT UNSIGNED NULL,

    -- Llave primaria: identifica a cada fila del detalle.
    CONSTRAINT pk_detalle_solicitud PRIMARY KEY (id),
    -- Un repuesto no se repite en la misma solicitud (RN-15).
    CONSTRAINT uq_detalle_solicitud_repuesto UNIQUE (solicitud_id, repuesto_id),
    -- La fila pertenece a una solicitud que debe existir.
    CONSTRAINT fk_detalle_solicitud_solicitud FOREIGN KEY (solicitud_id)
        REFERENCES solicitudes (id) ON DELETE RESTRICT,
    -- El repuesto pedido debe existir en el catálogo.
    CONSTRAINT fk_detalle_solicitud_repuesto FOREIGN KEY (repuesto_id)
        REFERENCES repuestos (id) ON DELETE RESTRICT,
    -- Si fue reemplazado, el reemplazo debe ser otra fila existente (RN-34).
    CONSTRAINT fk_detalle_solicitud_reemplazo FOREIGN KEY (reemplazado_por_id)
        REFERENCES detalle_solicitud (id) ON DELETE RESTRICT,
    -- La cantidad pedida debe ser mayor que cero (RN-11).
    CONSTRAINT ck_detalle_solicitud_cantidad CHECK (cantidad_solicitada > 0),
    -- Ninguna cantidad de control puede ser negativa.
    CONSTRAINT ck_detalle_solicitud_no_negativas CHECK (
        cantidad_apartada >= 0 AND cantidad_entregada >= 0 AND cantidad_devuelta >= 0
    ),
    -- No se puede entregar más de lo solicitado (RN-16).
    CONSTRAINT ck_detalle_solicitud_entregada CHECK (cantidad_entregada <= cantidad_solicitada),
    -- No se puede devolver más de lo entregado (RN-28).
    CONSTRAINT ck_detalle_solicitud_devuelta CHECK (cantidad_devuelta <= cantidad_entregada),
    -- Lo apartado más lo entregado no puede pasar de lo solicitado (RN-13).
    CONSTRAINT ck_detalle_solicitud_apartada CHECK (cantidad_apartada + cantidad_entregada <= cantidad_solicitada)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 6. Entregas (remisiones) y su detalle
-- ---------------------------------------------------------------------

-- Tabla entregas: cada entrega de repuestos. Cada fila es una remisión.
-- Una entrega no se borra ni se edita: si fue un error, se retracta (RN-19, RN-26).
CREATE TABLE entregas (
    id                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    -- Número de remisión, por ejemplo REM-000124 (RN-18).
    numero_remision   VARCHAR(12) NOT NULL,
    solicitud_id      INT UNSIGNED NOT NULL,
    -- Contratista que recibió en ese momento; no cambia si se reasigna (RN-31).
    contratista_id    INT UNSIGNED NOT NULL,
    -- Admin que registró la entrega; lo pone el sistema (RN-20).
    registrado_por    INT UNSIGNED NOT NULL,
    -- Fecha y hora de la entrega; la pone el sistema (RN-20).
    registrado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- 1 = la entrega fue retractada (HU-31).
    retractada        TINYINT(1) NOT NULL DEFAULT 0,
    motivo_retraccion VARCHAR(255) NULL,
    retractada_por    INT UNSIGNED NULL,
    retractada_en     DATETIME NULL,

    -- Llave primaria: identifica a cada entrega.
    CONSTRAINT pk_entregas PRIMARY KEY (id),
    -- El número de remisión no se repite (RN-18).
    CONSTRAINT uq_entregas_numero_remision UNIQUE (numero_remision),
    -- La entrega pertenece a una solicitud que debe existir.
    CONSTRAINT fk_entregas_solicitud FOREIGN KEY (solicitud_id)
        REFERENCES solicitudes (id) ON DELETE RESTRICT,
    -- El contratista que recibió debe existir.
    CONSTRAINT fk_entregas_contratista FOREIGN KEY (contratista_id)
        REFERENCES contratistas (id) ON DELETE RESTRICT,
    -- Quien registró la entrega debe ser un usuario existente.
    CONSTRAINT fk_entregas_registrado_por FOREIGN KEY (registrado_por)
        REFERENCES usuarios (id) ON DELETE RESTRICT,
    -- Quien retractó la entrega, si aplica, debe ser un usuario existente.
    CONSTRAINT fk_entregas_retractada_por FOREIGN KEY (retractada_por)
        REFERENCES usuarios (id) ON DELETE RESTRICT,
    -- Si la entrega está retractada, deben quedar el motivo, quién y cuándo (RN-26).
    CONSTRAINT ck_entregas_retraccion CHECK (
        retractada = 0
        OR (motivo_retraccion IS NOT NULL AND TRIM(motivo_retraccion) <> ''
            AND retractada_por IS NOT NULL AND retractada_en IS NOT NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Tabla detalle_entrega: los repuestos y cantidades de cada entrega.
CREATE TABLE detalle_entrega (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    entrega_id  INT UNSIGNED NOT NULL,
    repuesto_id INT UNSIGNED NOT NULL,
    cantidad    DECIMAL(12,2) NOT NULL,

    -- Llave primaria: identifica a cada fila del detalle.
    CONSTRAINT pk_detalle_entrega PRIMARY KEY (id),
    -- Un repuesto aparece una sola vez en cada entrega.
    CONSTRAINT uq_detalle_entrega_repuesto UNIQUE (entrega_id, repuesto_id),
    -- La fila pertenece a una entrega que debe existir.
    CONSTRAINT fk_detalle_entrega_entrega FOREIGN KEY (entrega_id)
        REFERENCES entregas (id) ON DELETE RESTRICT,
    -- El repuesto entregado debe existir en el catálogo.
    CONSTRAINT fk_detalle_entrega_repuesto FOREIGN KEY (repuesto_id)
        REFERENCES repuestos (id) ON DELETE RESTRICT,
    -- La cantidad entregada debe ser mayor que cero (RN-11).
    CONSTRAINT ck_detalle_entrega_cantidad CHECK (cantidad > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 7. Entradas al almacén y devoluciones
-- ---------------------------------------------------------------------

-- Tabla entradas_almacen: la mercancía que llega al almacén.
-- Una entrada no se borra: si fue un error, se retracta (HU-32, RN-26).
CREATE TABLE entradas_almacen (
    id                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    repuesto_id       INT UNSIGNED NOT NULL,
    cantidad          DECIMAL(12,2) NOT NULL,
    -- Nota opcional; puede incluir el número de factura (PA-11).
    observacion       VARCHAR(255) NULL,
    registrado_por    INT UNSIGNED NOT NULL,
    registrado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- 1 = la entrada fue retractada.
    retractada        TINYINT(1) NOT NULL DEFAULT 0,
    motivo_retraccion VARCHAR(255) NULL,
    retractada_por    INT UNSIGNED NULL,
    retractada_en     DATETIME NULL,

    -- Llave primaria: identifica a cada entrada.
    CONSTRAINT pk_entradas_almacen PRIMARY KEY (id),
    -- El repuesto que llegó debe existir en el catálogo.
    CONSTRAINT fk_entradas_almacen_repuesto FOREIGN KEY (repuesto_id)
        REFERENCES repuestos (id) ON DELETE RESTRICT,
    -- Quien registró la entrada debe ser un usuario existente.
    CONSTRAINT fk_entradas_almacen_registrado_por FOREIGN KEY (registrado_por)
        REFERENCES usuarios (id) ON DELETE RESTRICT,
    -- Quien retractó la entrada, si aplica, debe ser un usuario existente.
    CONSTRAINT fk_entradas_almacen_retractada_por FOREIGN KEY (retractada_por)
        REFERENCES usuarios (id) ON DELETE RESTRICT,
    -- La cantidad que llega debe ser mayor que cero (RN-11).
    CONSTRAINT ck_entradas_almacen_cantidad CHECK (cantidad > 0),
    -- Si la entrada está retractada, deben quedar el motivo, quién y cuándo (RN-26).
    CONSTRAINT ck_entradas_almacen_retraccion CHECK (
        retractada = 0
        OR (motivo_retraccion IS NOT NULL AND TRIM(motivo_retraccion) <> ''
            AND retractada_por IS NOT NULL AND retractada_en IS NOT NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Tabla devoluciones: repuestos que el contratista devuelve sin usar (HU-33).
CREATE TABLE devoluciones (
    id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
    solicitud_id   INT UNSIGNED NOT NULL,
    repuesto_id    INT UNSIGNED NOT NULL,
    cantidad       DECIMAL(12,2) NOT NULL,
    observacion    VARCHAR(255) NULL,
    registrado_por INT UNSIGNED NOT NULL,
    registrado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Llave primaria: identifica a cada devolución.
    CONSTRAINT pk_devoluciones PRIMARY KEY (id),
    -- La devolución es de una solicitud que debe existir.
    CONSTRAINT fk_devoluciones_solicitud FOREIGN KEY (solicitud_id)
        REFERENCES solicitudes (id) ON DELETE RESTRICT,
    -- El repuesto devuelto debe existir en el catálogo.
    CONSTRAINT fk_devoluciones_repuesto FOREIGN KEY (repuesto_id)
        REFERENCES repuestos (id) ON DELETE RESTRICT,
    -- Quien registró la devolución debe ser un usuario existente.
    CONSTRAINT fk_devoluciones_registrado_por FOREIGN KEY (registrado_por)
        REFERENCES usuarios (id) ON DELETE RESTRICT,
    -- La cantidad devuelta debe ser mayor que cero (RN-11).
    CONSTRAINT ck_devoluciones_cantidad CHECK (cantidad > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 8. Trazabilidad: movimientos de inventario e historial
-- ---------------------------------------------------------------------

-- Tabla movimientos_inventario: cada cambio de stock de un repuesto,
-- con el stock que quedó después. Permite explicar el stock actual (HU-27).
CREATE TABLE movimientos_inventario (
    id               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    repuesto_id      INT UNSIGNED NOT NULL,
    -- Qué causó el movimiento (RN-09).
    tipo             ENUM('entrada', 'entrega', 'devolucion', 'retraccion_entrada', 'retraccion_entrega') NOT NULL,
    -- Positiva si el stock sube; negativa si baja.
    cantidad         DECIMAL(12,2) NOT NULL,
    -- Stock en almacén después del movimiento.
    stock_resultante DECIMAL(12,2) NOT NULL,
    -- Origen del movimiento: solo uno de estos tres se llena.
    entrada_id       INT UNSIGNED NULL,
    entrega_id       INT UNSIGNED NULL,
    devolucion_id    INT UNSIGNED NULL,
    usuario_id       INT UNSIGNED NOT NULL,
    creado_en        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Llave primaria: identifica a cada movimiento.
    CONSTRAINT pk_movimientos_inventario PRIMARY KEY (id),
    -- El repuesto afectado debe existir en el catálogo.
    CONSTRAINT fk_movimientos_repuesto FOREIGN KEY (repuesto_id)
        REFERENCES repuestos (id) ON DELETE RESTRICT,
    -- Si el origen es una entrada, esa entrada debe existir.
    CONSTRAINT fk_movimientos_entrada FOREIGN KEY (entrada_id)
        REFERENCES entradas_almacen (id) ON DELETE RESTRICT,
    -- Si el origen es una entrega, esa entrega debe existir.
    CONSTRAINT fk_movimientos_entrega FOREIGN KEY (entrega_id)
        REFERENCES entregas (id) ON DELETE RESTRICT,
    -- Si el origen es una devolución, esa devolución debe existir.
    CONSTRAINT fk_movimientos_devolucion FOREIGN KEY (devolucion_id)
        REFERENCES devoluciones (id) ON DELETE RESTRICT,
    -- Quien hizo el movimiento debe ser un usuario existente (RN-20).
    CONSTRAINT fk_movimientos_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios (id) ON DELETE RESTRICT,
    -- Un movimiento siempre cambia el stock: la cantidad no puede ser cero.
    CONSTRAINT ck_movimientos_cantidad CHECK (cantidad <> 0),
    -- Después de cualquier movimiento, el stock nunca queda negativo (RN-10).
    CONSTRAINT ck_movimientos_stock_resultante CHECK (stock_resultante >= 0),
    -- Cada tipo de movimiento debe indicar su origen correcto.
    CONSTRAINT ck_movimientos_origen CHECK (
        (tipo IN ('entrada', 'retraccion_entrada') AND entrada_id IS NOT NULL)
        OR (tipo IN ('entrega', 'retraccion_entrega') AND entrega_id IS NOT NULL)
        OR (tipo = 'devolucion' AND devolucion_id IS NOT NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Tabla historial_solicitud: la línea de tiempo de cada solicitud.
-- Guarda qué pasó, quién lo hizo y cuándo (RN-20).
CREATE TABLE historial_solicitud (
    id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    solicitud_id INT UNSIGNED NOT NULL,
    accion       ENUM('creada', 'editada', 'entrega', 'retraccion_entrega', 'devolucion',
                      'reparado', 'devuelto', 'anulada', 'reabierta',
                      'contratista_reasignado', 'repuesto_reemplazado') NOT NULL,
    -- Valor anterior y nuevo, o la remisión relacionada.
    detalle      VARCHAR(255) NULL,
    -- Motivo, cuando la acción lo exige (RN-23, RN-26, RN-29, RN-30).
    motivo       VARCHAR(255) NULL,
    usuario_id   INT UNSIGNED NOT NULL,
    creado_en    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Llave primaria: identifica a cada registro del historial.
    CONSTRAINT pk_historial_solicitud PRIMARY KEY (id),
    -- El registro pertenece a una solicitud que debe existir.
    CONSTRAINT fk_historial_solicitud FOREIGN KEY (solicitud_id)
        REFERENCES solicitudes (id) ON DELETE RESTRICT,
    -- Quien hizo la acción debe ser un usuario existente (RN-20).
    CONSTRAINT fk_historial_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios (id) ON DELETE RESTRICT,
    -- Las acciones que exigen motivo no se pueden guardar sin él.
    CONSTRAINT ck_historial_motivo CHECK (
        accion NOT IN ('retraccion_entrega', 'devuelto', 'anulada', 'reabierta')
        OR (motivo IS NOT NULL AND TRIM(motivo) <> '')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 9. Datos mínimos para que el sistema funcione
-- ---------------------------------------------------------------------

-- Los dos contadores empiezan en 0: la primera solicitud será SOL-000001
-- y la primera remisión será REM-000001. Sin estas filas, la API no puede
-- generar números. Los datos de prueba van en database/seed.sql.
INSERT INTO consecutivos (tipo, ultimo_numero) VALUES
    ('SOL', 0),
    ('REM', 0);
