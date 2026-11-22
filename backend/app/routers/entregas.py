"""
Archivo:  backend/app/routers/entregas.py
Proyecto: FacturApp (backend)

Qué hace:
    Las rutas de entregas y remisiones:
        POST /api/solicitudes/{id}/entregas   registrar una entrega (solo Admin, HU-21)
        GET  /api/entregas                    listar entregas; ?solicitud_id= filtra (todos)
        GET  /api/entregas/{id}               la remisión para ver o imprimir (todos, HU-24)
        GET  /api/entregas/{id}/remision      lo mismo, con el nombre del contrato del Entregable 04

    No hay ruta para editar ni borrar una entrega: una remisión no se
    cambia (RN-19); si hubo un error, se retracta (HU-31, pendiente).
"""

from typing import Any

from fastapi import APIRouter, Depends, status

from app.core.dependencias import requiere_admin, usuario_actual
from app.db.conexion import obtener_conexion
from app.repositories.tablas import Usuario
from app.schemas.entregas import EntregaEntrada, EntregaResumen, RemisionSalida
from app.services import entregas_service

router = APIRouter(tags=["entregas"])


@router.post("/solicitudes/{solicitud_id}/entregas", response_model=RemisionSalida,
             status_code=status.HTTP_201_CREATED)
def registrar_entrega(solicitud_id: int, datos: EntregaEntrada, admin: Usuario = Depends(requiere_admin),
                      conexion: Any = Depends(obtener_conexion)):
    """Registra la entrega en una sola transacción y devuelve su remisión."""
    return entregas_service.registrar(conexion, solicitud_id, datos, admin)


@router.get("/entregas", response_model=list[EntregaResumen])
def listar_entregas(solicitud_id: int | None = None, _u: Usuario = Depends(usuario_actual),
                    conexion: Any = Depends(obtener_conexion)):
    """Lista las entregas, de la más reciente a la más antigua."""
    return entregas_service.listar(conexion, solicitud_id)


@router.get("/entregas/{entrega_id}", response_model=RemisionSalida)
@router.get("/entregas/{entrega_id}/remision", response_model=RemisionSalida)
def ver_remision(entrega_id: int, _u: Usuario = Depends(usuario_actual), conexion: Any = Depends(obtener_conexion)):
    """Devuelve la remisión con contratista, usuario y repuestos."""
    return entregas_service.obtener_remision(conexion, entrega_id)
