"""
Archivo:  backend/app/repositories/tablas.py
Proyecto: FacturApp (backend)

Qué hace:
    Describe en Python las 14 tablas de la base de datos "facturapp",
    exactamente como están en database/schema.sql: mismos nombres de
    tablas y columnas, en el mismo orden, con su tipo SQL, si aceptan
    valores vacíos (NULL) y a qué tabla apuntan sus llaves foráneas.

Qué NO hace:
    No crea ni modifica tablas. La base de datos ya existe y se crea
    solo con database/schema.sql. Aquí no hay ORM (decisión del
    proyecto): las consultas se escriben con SQL directo en los
    repositories.

Para qué sirve:
    1. Convertir cada fila que devuelve la base de datos en un objeto con
       tipos claros (por ejemplo, Repuesto.stock_almacen es un Decimal).
    2. Comprobar con una prueba (tests/test_tablas.py) que este archivo y
       la base de datos real dicen lo mismo.

Conceptos:
    - dataclass: una clase que solo guarda datos; Python crea solo el
      constructor. Cada atributo es una columna.
    - Tipos: int = número entero, str = texto, Decimal = número con
      decimales exactos (para cantidades), datetime = fecha y hora,
      date = fecha, bool = sí o no (en la base es TINYINT(1): 1 o 0).
    - Optional[...] (o "| None"): la columna acepta NULL.
    - Literal[...]: la columna solo acepta esos valores (ENUM en SQL).
    - columna(sql, fk): guarda junto al atributo su tipo SQL exacto y,
      si es llave foránea, la tabla y columna a la que apunta.
"""

from dataclasses import dataclass, field, fields
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal


def columna(sql: str, fk: str | None = None) -> Any:
    """Describe una columna: su tipo SQL exacto y, si aplica, su llave foránea ("tabla.columna")."""
    return field(metadata={"sql": sql, "fk": fk})


# Tipos de las listas cerradas (ENUM) de schema.sql.
Rol = Literal["admin", "oficina"]
UnidadMedida = Literal["unidad", "metro", "litro", "kilogramo"]
EstadoSolicitud = Literal["abierta", "reparado", "devuelto", "anulada"]
TipoMovimiento = Literal["entrada", "entrega", "devolucion", "retraccion_entrada", "retraccion_entrega"]
AccionHistorial = Literal[
    "creada", "editada", "entrega", "retraccion_entrega", "devolucion",
    "reparado", "devuelto", "anulada", "reabierta",
    "contratista_reasignado", "repuesto_reemplazado",
]


# ---------------------------------------------------------------- tablas base

@dataclass
class Usuario:
    """Tabla usuarios: personas que entran al sistema."""
    id: int = columna("int unsigned")
    nombre: str = columna("varchar(100)")
    correo: str = columna("varchar(150)")
    contrasena_hash: str = columna("varchar(255)")
    rol: Rol = columna("enum('admin','oficina')")
    activo: bool = columna("tinyint(1)")
    debe_cambiar_contrasena: bool = columna("tinyint(1)")
    creado_en: datetime = columna("datetime")


@dataclass
class Categoria:
    """Tabla categorias: agrupan los repuestos."""
    id: int = columna("int unsigned")
    nombre: str = columna("varchar(80)")
    activo: bool = columna("tinyint(1)")


@dataclass
class Contratista:
    """Tabla contratistas: técnicos o empresas que reciben los repuestos."""
    id: int = columna("int unsigned")
    documento: str = columna("varchar(20)")
    documento_normalizado: str = columna("varchar(20)")
    nombre: str = columna("varchar(120)")
    telefono: str | None = columna("varchar(20)")
    activo: bool = columna("tinyint(1)")


@dataclass
class Consecutivo:
    """Tabla consecutivos: último número usado de SOL y REM (RN-18)."""
    tipo: str = columna("varchar(10)")
    ultimo_numero: int = columna("int unsigned")


# ---------------------------------------------------------------- catálogos

@dataclass
class Repuesto:
    """Tabla repuestos: catálogo con su stock."""
    id: int = columna("int unsigned")
    codigo: str = columna("varchar(30)")
    nombre: str = columna("varchar(120)")
    categoria_id: int = columna("int unsigned", fk="categorias.id")
    unidad_medida: UnidadMedida = columna("enum('unidad','metro','litro','kilogramo')")
    stock_almacen: Decimal = columna("decimal(12,2)")
    stock_apartado: Decimal = columna("decimal(12,2)")
    stock_minimo: Decimal | None = columna("decimal(12,2)")
    activo: bool = columna("tinyint(1)")


@dataclass
class Equipo:
    """Tabla equipos: las neveras que se reparan."""
    id: int = columna("int unsigned")
    codigo: str = columna("varchar(30)")
    descripcion: str | None = columna("varchar(150)")
    activo: bool = columna("tinyint(1)")
    creado_por: int = columna("int unsigned", fk="usuarios.id")
    creado_en: datetime = columna("datetime")


# ---------------------------------------------------------------- solicitudes

@dataclass
class Solicitud:
    """Tabla solicitudes: cada solicitud de repuestos."""
    id: int = columna("int unsigned")
    numero: str = columna("varchar(12)")
    equipo_id: int = columna("int unsigned", fk="equipos.id")
    contratista_id: int = columna("int unsigned", fk="contratistas.id")
    fecha_entrega: date = columna("date")
    estado: EstadoSolicitud = columna("enum('abierta','reparado','devuelto','anulada')")
    motivo_cierre: str | None = columna("varchar(255)")
    creado_por: int = columna("int unsigned", fk="usuarios.id")
    creado_en: datetime = columna("datetime")


@dataclass
class DetalleSolicitud:
    """Tabla detalle_solicitud: los repuestos de cada solicitud."""
    id: int = columna("int unsigned")
    solicitud_id: int = columna("int unsigned", fk="solicitudes.id")
    repuesto_id: int = columna("int unsigned", fk="repuestos.id")
    cantidad_solicitada: Decimal = columna("decimal(12,2)")
    cantidad_apartada: Decimal = columna("decimal(12,2)")
    cantidad_entregada: Decimal = columna("decimal(12,2)")
    cantidad_devuelta: Decimal = columna("decimal(12,2)")
    cantidad_reemplazada: Decimal = columna("decimal(12,2)")
    reemplazado_por_id: int | None = columna("int unsigned", fk="detalle_solicitud.id")


# ---------------------------------------------------------------- entregas

@dataclass
class Entrega:
    """Tabla entregas: cada entrega; cada fila es una remisión."""
    id: int = columna("int unsigned")
    numero_remision: str = columna("varchar(12)")
    solicitud_id: int = columna("int unsigned", fk="solicitudes.id")
    contratista_id: int = columna("int unsigned", fk="contratistas.id")
    registrado_por: int = columna("int unsigned", fk="usuarios.id")
    registrado_en: datetime = columna("datetime")
    retractada: bool = columna("tinyint(1)")
    motivo_retraccion: str | None = columna("varchar(255)")
    retractada_por: int | None = columna("int unsigned", fk="usuarios.id")
    retractada_en: datetime | None = columna("datetime")


@dataclass
class DetalleEntrega:
    """Tabla detalle_entrega: repuestos y cantidades de cada entrega."""
    id: int = columna("int unsigned")
    entrega_id: int = columna("int unsigned", fk="entregas.id")
    repuesto_id: int = columna("int unsigned", fk="repuestos.id")
    cantidad: Decimal = columna("decimal(12,2)")


# ---------------------------------------------------------------- almacén

@dataclass
class EntradaAlmacen:
    """Tabla entradas_almacen: mercancía que llega al almacén."""
    id: int = columna("int unsigned")
    repuesto_id: int = columna("int unsigned", fk="repuestos.id")
    cantidad: Decimal = columna("decimal(12,2)")
    observacion: str | None = columna("varchar(255)")
    registrado_por: int = columna("int unsigned", fk="usuarios.id")
    registrado_en: datetime = columna("datetime")
    retractada: bool = columna("tinyint(1)")
    motivo_retraccion: str | None = columna("varchar(255)")
    retractada_por: int | None = columna("int unsigned", fk="usuarios.id")
    retractada_en: datetime | None = columna("datetime")


@dataclass
class Devolucion:
    """Tabla devoluciones: repuestos devueltos sin usar."""
    id: int = columna("int unsigned")
    solicitud_id: int = columna("int unsigned", fk="solicitudes.id")
    repuesto_id: int = columna("int unsigned", fk="repuestos.id")
    cantidad: Decimal = columna("decimal(12,2)")
    observacion: str | None = columna("varchar(255)")
    registrado_por: int = columna("int unsigned", fk="usuarios.id")
    registrado_en: datetime = columna("datetime")


# ---------------------------------------------------------------- trazabilidad

@dataclass
class MovimientoInventario:
    """Tabla movimientos_inventario: cada cambio de stock."""
    id: int = columna("int unsigned")
    repuesto_id: int = columna("int unsigned", fk="repuestos.id")
    tipo: TipoMovimiento = columna(
        "enum('entrada','entrega','devolucion','retraccion_entrada','retraccion_entrega')"
    )
    cantidad: Decimal = columna("decimal(12,2)")
    stock_resultante: Decimal = columna("decimal(12,2)")
    entrada_id: int | None = columna("int unsigned", fk="entradas_almacen.id")
    entrega_id: int | None = columna("int unsigned", fk="entregas.id")
    devolucion_id: int | None = columna("int unsigned", fk="devoluciones.id")
    usuario_id: int = columna("int unsigned", fk="usuarios.id")
    creado_en: datetime = columna("datetime")


@dataclass
class HistorialSolicitud:
    """Tabla historial_solicitud: la línea de tiempo de cada solicitud."""
    id: int = columna("int unsigned")
    solicitud_id: int = columna("int unsigned", fk="solicitudes.id")
    accion: AccionHistorial = columna(
        "enum('creada','editada','entrega','retraccion_entrega','devolucion',"
        "'reparado','devuelto','anulada','reabierta','contratista_reasignado','repuesto_reemplazado')"
    )
    detalle: str | None = columna("varchar(255)")
    motivo: str | None = columna("varchar(255)")
    usuario_id: int = columna("int unsigned", fk="usuarios.id")
    creado_en: datetime = columna("datetime")


# ---------------------------------------------------------------- registro de tablas

# Nombre de cada tabla en la base de datos y su modelo, en el mismo orden
# en que schema.sql las crea. Sirve también como lista de nombres
# permitidos: los nombres de tabla no pueden ir como parámetro (%s) en
# SQL, así que solo se aceptan los que están aquí.
TABLAS: dict[str, type] = {
    "usuarios": Usuario,
    "categorias": Categoria,
    "contratistas": Contratista,
    "consecutivos": Consecutivo,
    "repuestos": Repuesto,
    "equipos": Equipo,
    "solicitudes": Solicitud,
    "detalle_solicitud": DetalleSolicitud,
    "entregas": Entrega,
    "detalle_entrega": DetalleEntrega,
    "entradas_almacen": EntradaAlmacen,
    "devoluciones": Devolucion,
    "movimientos_inventario": MovimientoInventario,
    "historial_solicitud": HistorialSolicitud,
}


def desde_fila(modelo: type, fila: dict[str, Any]) -> Any:
    """Convierte una fila de la base de datos (diccionario) en un objeto del modelo.

    Las columnas TINYINT(1) llegan como 1 o 0 y aquí se convierten en
    True o False.
    """
    datos = {}
    for campo in fields(modelo):
        valor = fila[campo.name]
        if campo.metadata["sql"] == "tinyint(1)" and valor is not None:
            valor = bool(valor)
        datos[campo.name] = valor
    return modelo(**datos)
