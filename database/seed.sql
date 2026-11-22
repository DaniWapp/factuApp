-- =====================================================================
-- Archivo:  database/seed.sql
-- Proyecto: FacturApp - Solicitud y entrega de repuestos de refrigeración
--
-- Qué hace:
--   Llena la base de datos "facturapp" con datos de ejemplo para probar
--   el sistema: usuarios, categorías, repuestos, contratistas, equipos,
--   dos solicitudes y dos entregas (una completa y una parcial).
--
-- Cuándo se ejecuta:
--   Justo DESPUÉS de database/schema.sql, con las tablas vacías.
--   Si las tablas ya tienen datos, vuelva a ejecutar primero schema.sql.
--
-- Cómo se ejecuta:
--   - Desde phpMyAdmin: pestaña "Importar" y elegir este archivo.
--   - Desde CMD o Git Bash (en la carpeta del proyecto):
--       mysql -u root -p --default-character-set=utf8mb4 < database/seed.sql
--   - Desde PowerShell:
--       cmd /c "mysql -u root -p --default-character-set=utf8mb4 < database\seed.sql"
--
-- Por qué los números cuadran:
--   El stock de cada repuesto se calcula así:
--     stock en almacén = lo que entró al almacén - lo que se entregó
--   y cada entrada y cada entrega deja su movimiento de inventario.
--   Al final del archivo hay una consulta para comprobarlo.
--
-- Todos los nombres, documentos y correos son ficticios.
-- =====================================================================

USE facturapp;

-- Todo el archivo se guarda como un solo bloque (transacción):
-- si una línea falla, no se guarda nada y la base queda limpia.
START TRANSACTION;


-- ---------------------------------------------------------------------
-- 1. Usuarios: 1 Admin y 2 de Oficina radicadora
-- ---------------------------------------------------------------------

-- IMPORTANTE SOBRE LAS CONTRASEÑAS:
-- El valor de contrasena_hash es un HASH DE EJEMPLO que no corresponde a
-- ninguna contraseña conocida: con estos datos nadie puede iniciar sesión
-- todavía. Las contraseñas reales se crearán desde el backend en el
-- Entregable 06, que las cifrará con bcrypt antes de guardarlas (RNF-01).
-- Nunca se escribe una contraseña real en un archivo SQL.
--
-- Aunque es de ejemplo, tiene el formato exacto de bcrypt (60 caracteres:
-- "$2b$12$" + 22 de sal + 31 de hash). Así, si alguien intenta entrar,
-- bcrypt responde "contraseña incorrecta" en lugar de fallar con un error.
INSERT INTO usuarios (id, nombre, correo, contrasena_hash, rol, activo, debe_cambiar_contrasena, creado_en) VALUES
    (1, 'Administrador del sistema', 'admin@facturapp.test',
        '$2b$12$HashDeEjemploNoValido.SeCreaRealmenteEnElBackendE06..', 'admin',   1, 0, '2026-11-02 08:00:00'),
    (2, 'Laura Gómez',               'laura.gomez@facturapp.test',
        '$2b$12$HashDeEjemploNoValido.SeCreaRealmenteEnElBackendE06..', 'oficina', 1, 0, '2026-11-02 08:10:00'),
    (3, 'Andrés Muñoz',              'andres.munoz@facturapp.test',
        '$2b$12$HashDeEjemploNoValido.SeCreaRealmenteEnElBackendE06..', 'oficina', 1, 0, '2026-11-02 08:15:00');


-- ---------------------------------------------------------------------
-- 2. Categorías de repuestos de refrigeración
-- ---------------------------------------------------------------------

INSERT INTO categorias (id, nombre, activo) VALUES
    (1, 'Compresores',           1),
    (2, 'Válvulas',              1),
    (3, 'Motores de ventilador', 1);


-- ---------------------------------------------------------------------
-- 3. Repuestos (6), con su stock ya actualizado
-- ---------------------------------------------------------------------

-- stock_almacen  = entradas al almacén (sección 6) - entregas (sección 9).
-- stock_apartado = lo reservado para la solicitud abierta SOL-000002.
--
-- Repuesto   Entró   Entregado   En almacén   Apartado
-- COM-001      10        1            9           0
-- COM-002       6        0            6           0
-- VAL-001      25        2           23           0
-- VAL-002      12        2           10           0
-- MOT-001      15        1           14           2
-- MOT-002      15        0           15           0
INSERT INTO repuestos (id, codigo, nombre, categoria_id, unidad_medida, stock_almacen, stock_apartado, stock_minimo, activo) VALUES
    (1, 'COM-001', 'Compresor hermético 1/2 HP R134a',          1, 'unidad',  9.00, 0.00, 2.00, 1),
    (2, 'COM-002', 'Compresor hermético 1/3 HP R600a',          1, 'unidad',  6.00, 0.00, 2.00, 1),
    (3, 'VAL-001', 'Válvula de expansión termostática',         2, 'unidad', 23.00, 0.00, 5.00, 1),
    (4, 'VAL-002', 'Válvula solenoide 1/4"',                    2, 'unidad', 10.00, 0.00, 3.00, 1),
    (5, 'MOT-001', 'Motor ventilador condensador 9 W',          3, 'unidad', 14.00, 2.00, 4.00, 1),
    (6, 'MOT-002', 'Motor ventilador evaporador 5 W',           3, 'unidad', 15.00, 0.00, 4.00, 1);


-- ---------------------------------------------------------------------
-- 4. Contratistas (3)
-- ---------------------------------------------------------------------

-- "documento" se guarda como se escribió y "documento_normalizado"
-- solo con dígitos; este último es el que no se puede repetir (RN-08).
INSERT INTO contratistas (id, documento, documento_normalizado, nombre, telefono, activo) VALUES
    (1, '900.456.789-1', '9004567891', 'Refrigeración Andina S.A.S.', '6014567890', 1),
    (2, '1.020.345.678', '1020345678', 'Carlos Pérez Rincón',         '3104567890', 1),
    (3, '901.234.567-3', '9012345673', 'Frío Técnico Ltda.',          '6042345678', 1);


-- ---------------------------------------------------------------------
-- 5. Equipos (neveras)
-- ---------------------------------------------------------------------

-- Las entregas necesitan una solicitud, y cada solicitud necesita un
-- equipo. Por eso se crean estos equipos aunque no se pidieron aparte.
INSERT INTO equipos (id, codigo, descripcion, activo, creado_por, creado_en) VALUES
    (1, 'NEV-0001', 'Nevera vertical 2 puertas - Punto de venta Centro', 1, 2, '2026-11-03 09:00:00'),
    (2, 'NEV-0002', 'Nevera horizontal 400 L - Punto de venta Norte',    1, 3, '2026-11-03 09:20:00'),
    (3, 'NEV-0003', 'Nevera exhibidora 1 puerta - Punto de venta Sur',   1, 2, '2026-11-03 09:40:00');


-- ---------------------------------------------------------------------
-- 6. Entradas al almacén (el stock inicial)
-- ---------------------------------------------------------------------

-- El stock no se escribe a mano (RN-09): llega con estas entradas.
INSERT INTO entradas_almacen (id, repuesto_id, cantidad, observacion, registrado_por, registrado_en) VALUES
    (1, 1, 10.00, 'Inventario inicial', 1, '2026-11-04 07:30:00'),
    (2, 2,  6.00, 'Inventario inicial', 1, '2026-11-04 07:31:00'),
    (3, 3, 25.00, 'Inventario inicial', 1, '2026-11-04 07:32:00'),
    (4, 4, 12.00, 'Inventario inicial', 1, '2026-11-04 07:33:00'),
    (5, 5, 15.00, 'Inventario inicial', 1, '2026-11-04 07:34:00'),
    (6, 6, 15.00, 'Inventario inicial', 1, '2026-11-04 07:35:00');


-- ---------------------------------------------------------------------
-- 7. Solicitudes (2)
-- ---------------------------------------------------------------------

-- SOL-000001: se entregó todo y el equipo quedó reparado.
-- SOL-000002: sigue abierta, con una entrega parcial.
INSERT INTO solicitudes (id, numero, equipo_id, contratista_id, fecha_entrega, estado, motivo_cierre, creado_por, creado_en) VALUES
    (1, 'SOL-000001', 1, 1, '2026-11-06', 'reparado', NULL, 2, '2026-11-05 10:00:00'),
    (2, 'SOL-000002', 2, 2, '2026-11-10', 'abierta',  NULL, 3, '2026-11-07 11:30:00');


-- ---------------------------------------------------------------------
-- 8. Detalle de las solicitudes
-- ---------------------------------------------------------------------

-- Para cada repuesto: cuánto se pidió, cuánto está apartado y cuánto
-- se entregó. Lo que está en espera se calcula:
-- solicitada - reemplazada - entregada - apartada.
-- cantidad_reemplazada no se escribe: queda en 0 (su valor por defecto).
INSERT INTO detalle_solicitud (id, solicitud_id, repuesto_id, cantidad_solicitada, cantidad_apartada, cantidad_entregada, cantidad_devuelta) VALUES
    -- SOL-000001: entrega completa.
    (1, 1, 1, 1.00, 0.00, 1.00, 0.00),   -- COM-001: pidió 1, entregado 1
    (2, 1, 3, 2.00, 0.00, 2.00, 0.00),   -- VAL-001: pidió 2, entregadas 2
    -- SOL-000002: entrega parcial.
    (3, 2, 4, 2.00, 0.00, 2.00, 0.00),   -- VAL-002: pidió 2, entregadas 2
    (4, 2, 5, 3.00, 2.00, 1.00, 0.00);   -- MOT-001: pidió 3, entregado 1, faltan 2 (apartados)


-- ---------------------------------------------------------------------
-- 9. Entregas (2) con su número de remisión
-- ---------------------------------------------------------------------

-- Cada entrega es una remisión. Las registra el Admin (usuario 1).
INSERT INTO entregas (id, numero_remision, solicitud_id, contratista_id, registrado_por, registrado_en, retractada) VALUES
    (1, 'REM-000001', 1, 1, 1, '2026-11-06 08:45:00', 0),
    (2, 'REM-000002', 2, 2, 1, '2026-11-08 14:20:00', 0);


-- ---------------------------------------------------------------------
-- 10. Detalle de las entregas
-- ---------------------------------------------------------------------

-- Qué repuesto y qué cantidad salió en cada remisión.
INSERT INTO detalle_entrega (id, entrega_id, repuesto_id, cantidad) VALUES
    (1, 1, 1, 1.00),   -- REM-000001: 1 compresor COM-001
    (2, 1, 3, 2.00),   -- REM-000001: 2 válvulas VAL-001
    (3, 2, 4, 2.00),   -- REM-000002: 2 válvulas VAL-002
    (4, 2, 5, 1.00);   -- REM-000002: 1 motor MOT-001 (entrega parcial)


-- ---------------------------------------------------------------------
-- 11. Movimientos de inventario
-- ---------------------------------------------------------------------

-- Cada entrada suma (cantidad positiva) y cada entrega resta
-- (cantidad negativa). stock_resultante es el stock que quedó después.
INSERT INTO movimientos_inventario (repuesto_id, tipo, cantidad, stock_resultante, entrada_id, entrega_id, devolucion_id, usuario_id, creado_en) VALUES
    -- Entradas del inventario inicial.
    (1, 'entrada', 10.00, 10.00, 1, NULL, NULL, 1, '2026-11-04 07:30:00'),
    (2, 'entrada',  6.00,  6.00, 2, NULL, NULL, 1, '2026-11-04 07:31:00'),
    (3, 'entrada', 25.00, 25.00, 3, NULL, NULL, 1, '2026-11-04 07:32:00'),
    (4, 'entrada', 12.00, 12.00, 4, NULL, NULL, 1, '2026-11-04 07:33:00'),
    (5, 'entrada', 15.00, 15.00, 5, NULL, NULL, 1, '2026-11-04 07:34:00'),
    (6, 'entrada', 15.00, 15.00, 6, NULL, NULL, 1, '2026-11-04 07:35:00'),
    -- Salidas de la remisión REM-000001.
    (1, 'entrega', -1.00,  9.00, NULL, 1, NULL, 1, '2026-11-06 08:45:00'),
    (3, 'entrega', -2.00, 23.00, NULL, 1, NULL, 1, '2026-11-06 08:45:00'),
    -- Salidas de la remisión REM-000002.
    (4, 'entrega', -2.00, 10.00, NULL, 2, NULL, 1, '2026-11-08 14:20:00'),
    (5, 'entrega', -1.00, 14.00, NULL, 2, NULL, 1, '2026-11-08 14:20:00');


-- ---------------------------------------------------------------------
-- 12. Historial de las solicitudes (línea de tiempo)
-- ---------------------------------------------------------------------

INSERT INTO historial_solicitud (solicitud_id, accion, detalle, motivo, usuario_id, creado_en) VALUES
    (1, 'creada',   'Solicitud SOL-000001 creada',                    NULL, 2, '2026-11-05 10:00:00'),
    (1, 'entrega',  'Remisión REM-000001: entrega completa',          NULL, 1, '2026-11-06 08:45:00'),
    (1, 'reparado', 'Equipo NEV-0001 reparado',                       NULL, 2, '2026-11-06 16:00:00'),
    (2, 'creada',   'Solicitud SOL-000002 creada',                    NULL, 3, '2026-11-07 11:30:00'),
    (2, 'entrega',  'Remisión REM-000002: entrega parcial, faltan 2 MOT-001', NULL, 1, '2026-11-08 14:20:00');


-- ---------------------------------------------------------------------
-- 13. Consecutivos
-- ---------------------------------------------------------------------

-- schema.sql los dejó en 0. Como ya existen SOL-000002 y REM-000002,
-- la próxima solicitud será SOL-000003 y la próxima remisión REM-000003.
UPDATE consecutivos SET ultimo_numero = 2 WHERE tipo = 'SOL';
UPDATE consecutivos SET ultimo_numero = 2 WHERE tipo = 'REM';


-- Guarda todo lo anterior de una sola vez.
COMMIT;


-- ---------------------------------------------------------------------
-- 14. Comprobación (solo lectura)
-- ---------------------------------------------------------------------

-- Compara el stock guardado en cada repuesto con la suma de sus
-- movimientos. La columna "cuadra" debe decir SI en las 6 filas.
SELECT r.codigo,
       r.stock_almacen,
       SUM(m.cantidad) AS suma_movimientos,
       IF(r.stock_almacen = SUM(m.cantidad), 'SI', 'NO') AS cuadra
FROM repuestos r
JOIN movimientos_inventario m ON m.repuesto_id = r.id
GROUP BY r.id, r.codigo, r.stock_almacen
ORDER BY r.codigo;
