"""
Archivo:  backend/app/schemas/catalogos.py
Proyecto: FacturApp (backend)

Qué hace:
    Forma y validación de los datos de categorías, repuestos,
    contratistas e inventario (Pydantic). Si un dato no cumple, la API
    responde 422 con el campo que falló, antes de tocar la base de datos.

Reglas que se revisan aquí (las que no necesitan la base de datos):
    - Nombres sin espacios en los extremos y sin quedar vacíos (RN-07).
    - Códigos y documentos solo con los caracteres permitidos (RN-25).
    - Cantidades mayores que cero, con máximo 2 decimales (RN-11).
    - El repuesto NO tiene campo de stock: el stock no se escribe a mano
      (RN-09). Si alguien lo envía, se ignora.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.comunes import CantidadEntrada, CantidadSalida, Codigo, Documento, texto, texto_opcional

UnidadMedida = Literal["unidad", "metro", "litro", "kilogramo"]


# ---------------------------------------------------------------- categorías

class CategoriaEntrada(BaseModel):
    """Datos para crear o editar una categoría."""
    nombre: texto(80)


class CategoriaSalida(BaseModel):
    """Una categoría, con cuántos repuestos activos tiene."""
    id: int
    nombre: str
    activo: bool
    repuestos_activos: int = 0


# ---------------------------------------------------------------- repuestos

class RepuestoEntrada(BaseModel):
    """Datos del catálogo de un repuesto. No incluye stock (RN-09)."""
    codigo: Codigo
    nombre: texto(120)
    categoria_id: int = Field(gt=0)
    unidad_medida: UnidadMedida


class RepuestoSalida(BaseModel):
    """Un repuesto del catálogo, SIN stock (la Oficina no ve el stock, RN-02)."""
    id: int
    codigo: str
    nombre: str
    categoria_id: int
    categoria: str
    unidad_medida: str
    activo: bool


# ---------------------------------------------------------------- contratistas

class ContratistaEntrada(BaseModel):
    """Datos para crear o editar un contratista."""
    documento: Documento
    nombre: texto(120)
    telefono: texto_opcional(20) = None


class ContratistaSalida(BaseModel):
    """Un contratista."""
    id: int
    documento: str
    nombre: str
    telefono: str | None
    activo: bool


# ---------------------------------------------------------------- inventario

class InventarioSalida(BaseModel):
    """Stock de un repuesto (solo Admin, HU-20)."""
    id: int
    codigo: str
    nombre: str
    unidad_medida: str
    stock_almacen: CantidadSalida
    stock_apartado: CantidadSalida
    disponible: CantidadSalida
    en_espera: CantidadSalida
    activo: bool


class EntradaAlmacenEntrada(BaseModel):
    """Datos de una entrada al almacén: la única forma de aumentar el stock (RN-09)."""
    repuesto_id: int = Field(gt=0)
    cantidad: CantidadEntrada
    observacion: texto_opcional(255) = None


class EntradaAlmacenSalida(BaseModel):
    """Una entrada al almacén registrada."""
    id: int
    repuesto_id: int
    codigo: str
    repuesto: str
    cantidad: CantidadSalida
    observacion: str | None
    registrado_por: int
    registrado_por_nombre: str
    registrado_en: datetime
    retractada: bool
    motivo_retraccion: str | None


class EntradaRegistradaSalida(BaseModel):
    """Respuesta al registrar una entrada: el stock nuevo y lo que se apartó para solicitudes en espera."""
    entrada_id: int
    repuesto_id: int
    stock_almacen: CantidadSalida
    apartado_para_solicitudes: CantidadSalida
