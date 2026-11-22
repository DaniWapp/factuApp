"""
Capa repositories: las consultas SQL.

Es la única capa que habla con las tablas. Usa PyMySQL con SQL directo y
siempre con parámetros (%s), nunca pegando texto del usuario (RNF-05).
"""
