"""
Capa schemas: forma de los datos que entran y salen de la API.

Cada archivo define clases de Pydantic. Pydantic revisa los datos
automáticamente: si falta un campo o una cantidad es negativa, la API
responde 422 antes de tocar la base de datos.

Ejemplo de lo que vendrá: schemas/entregas.py con EntregaCrear y EntregaRespuesta.
"""
