"""
Capa routers: las rutas (endpoints) de la API.

Cada archivo agrupa las rutas de un módulo (salud, repuestos, entregas...).
Un router recibe la petición, llama al service que corresponde y devuelve
la respuesta en JSON. Nunca escribe SQL (RNF-23).
"""
