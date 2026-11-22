"""
Archivo:  backend/app/core/errores.py
Proyecto: FacturApp (backend)

Qué hace:
    1. Define los errores de la API (ErrorApi y sus tipos), cada uno con
       su código HTTP, un código corto para el programa y un mensaje para
       la persona.
    2. Registra los "manejadores" que convierten cualquier error en el
       formato único de la API (Entregable 04, sección 7):

           {"error": {"codigo": "...", "mensaje": "...", "campos": null}}

Conceptos:
    - Lanzar un error (raise): detiene lo que se estaba haciendo. Un
      service lanza, por ejemplo, Conflicto("CORREO_REPETIDO", "...") y el
      manejador lo convierte en una respuesta 409 con ese formato.
    - Manejador de excepciones (exception_handler): una función que
      FastAPI llama cuando ocurre un tipo de error.
    - RequestValidationError: el error que lanza FastAPI cuando los datos
      no cumplen el schema de Pydantic (422) o el JSON está roto (400).
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


# ---------------------------------------------------------------- errores de la API

class ErrorApi(Exception):
    """Error base de la API. Cada subclase fija su código HTTP."""

    estado_http = 500

    def __init__(self, codigo: str, mensaje: str, campos: dict[str, str] | None = None):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
        self.campos = campos


class NoAutenticado(ErrorApi):
    """401: no se sabe quién es, la sesión venció o el usuario fue desactivado."""
    estado_http = 401


class SinPermiso(ErrorApi):
    """403: se sabe quién es, pero su rol no puede hacer esta acción (RN-02)."""
    estado_http = 403


class NoEncontrado(ErrorApi):
    """404: el registro pedido no existe."""
    estado_http = 404


class Conflicto(ErrorApi):
    """409: los datos son válidos, pero chocan con una regla de negocio."""
    estado_http = 409


# ---------------------------------------------------------------- formato único

def respuesta_error(estado_http: int, codigo: str, mensaje: str,
                    campos: dict[str, str] | None = None) -> JSONResponse:
    """Arma la respuesta JSON con el formato único de errores."""
    return JSONResponse(
        status_code=estado_http,
        content={"error": {"codigo": codigo, "mensaje": mensaje, "campos": campos}},
    )


# Mensajes en español para los errores de validación más comunes de Pydantic.
def mensaje_de_validacion(error: dict[str, Any]) -> str:
    """Traduce un error de validación de Pydantic a un mensaje sencillo en español."""
    tipo = error.get("type", "")
    contexto = error.get("ctx") or {}
    if tipo == "missing":
        return "Este dato es obligatorio."
    if tipo == "string_too_short":
        return "Escriba este dato."
    if tipo == "string_too_long":
        return f"Máximo {contexto.get('max_length')} caracteres."
    if tipo == "literal_error":
        return "Valor no permitido."
    if tipo in ("bool_parsing", "bool_type"):
        return "Debe ser verdadero o falso."
    if tipo == "value_error":
        # Los validadores propios lanzan ValueError con el mensaje ya escrito.
        return str(contexto.get("error", error.get("msg", "Revise este dato.")))
    return "Revise este dato."


def registrar_manejadores(app: FastAPI) -> None:
    """Conecta los manejadores de errores con la aplicación."""

    @app.exception_handler(ErrorApi)
    async def manejar_error_api(_request: Request, error: ErrorApi) -> JSONResponse:
        """Errores lanzados por la API (401, 403, 404, 409)."""
        return respuesta_error(error.estado_http, error.codigo, error.mensaje, error.campos)

    @app.exception_handler(RequestValidationError)
    async def manejar_validacion(_request: Request, error: RequestValidationError) -> JSONResponse:
        """Datos que no cumplen el schema (422) o JSON mal armado (400)."""
        errores = error.errors()
        if any(e.get("type") == "json_invalid" for e in errores):
            return respuesta_error(400, "PETICION_INVALIDA", "La petición está mal armada.")
        campos = {}
        for e in errores:
            # "loc" dice dónde está el error, por ejemplo ("body", "correo").
            nombre = ".".join(str(parte) for parte in e["loc"] if parte != "body")
            campos[nombre or "datos"] = mensaje_de_validacion(e)
        return respuesta_error(422, "DATOS_INVALIDOS", "Revise los datos marcados.", campos)

    @app.exception_handler(StarletteHTTPException)
    async def manejar_http(_request: Request, error: StarletteHTTPException) -> JSONResponse:
        """Errores propios de FastAPI, como una ruta que no existe (404) o un método no permitido (405)."""
        codigos = {404: ("NO_ENCONTRADO", "La dirección pedida no existe."),
                   405: ("METODO_NO_PERMITIDO", "Esta acción no está permitida en esta dirección.")}
        codigo, mensaje = codigos.get(error.status_code, ("ERROR", str(error.detail)))
        return respuesta_error(error.status_code, codigo, mensaje)
