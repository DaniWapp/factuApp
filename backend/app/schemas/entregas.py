"""
Archivo:  backend/app/schemas/entregas.py
Proyecto: FacturApp (backend)

Qué hace:
    Forma y validación de los datos de las entregas.

Lo que se revisa aquí, sin consultar la base de datos:
    - Al menos un repuesto (RN-15).
    - Cantidades mayores que cero, con máximo 2 decimales (RN-11).
    - Un repuesto no se repite en la misma entrega.
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.comunes import CantidadEntrada, CantidadSalida


class RepuestoAEntregar(BaseModel):
    """Un repuesto de la entrega y su cantidad."""
    repuesto_id: int = Field(gt=0)
    cantidad: CantidadEntrada


class EntregaEntrada(BaseModel):
    """Datos para registrar una entrega. El contratista, la fecha y el usuario NO se envían:
    el contratista sale de la solicitud, y la fecha y el usuario los pone el sistema (RN-20)."""
    repuestos: list[RepuestoAEntregar] = Field(min_length=1)

    @field_validator("repuestos")
    @classmethod
    def sin_repetidos(cls, repuestos: list[RepuestoAEntregar]) -> list[RepuestoAEntregar]:
        """Un repuesto no puede aparecer dos veces en la misma entrega."""
        ids = [r.repuesto_id for r in repuestos]
        if len(ids) != len(set(ids)):
            raise ValueError("Un repuesto no puede aparecer dos veces en la misma entrega.")
        return repuestos


class EntregaResumen(BaseModel):
    """Una entrega en la lista."""
    id: int
    numero_remision: str
    solicitud_id: int
    solicitud: str
    contratista: str
    registrado_por: str
    registrado_en: datetime
    retractada: bool
    repuestos: int


class PersonaRemision(BaseModel):
    """Contratista que recibe (con su documento) o usuario que entrega."""
    id: int
    nombre: str
    documento: str | None = None
    telefono: str | None = None


class RepuestoRemision(BaseModel):
    """Un repuesto entregado, como aparece en la remisión."""
    repuesto_id: int
    codigo: str
    nombre: str
    unidad_medida: str
    cantidad: CantidadSalida


class RemisionSalida(BaseModel):
    """Todo lo necesario para ver e imprimir la remisión (HU-24)."""
    id: int
    numero_remision: str
    registrado_en: datetime
    solicitud_id: int
    solicitud_numero: str
    equipo_codigo: str
    equipo_descripcion: str | None
    contratista: PersonaRemision
    registrado_por: PersonaRemision
    repuestos: list[RepuestoRemision]
    retractada: bool
    motivo_retraccion: str | None
    estado_entrega: str | None = None  # solo al registrar: "Parcial" o "Completa" (RN-21)
