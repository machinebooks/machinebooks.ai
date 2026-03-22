# Extraído de: LibroFinOps/cap-25-caso-tokens.md
# Reglas de routing: operación × complejidad → modelo
REGLAS_ROUTING = {
    # Clasificación: siempre haiku (tarea de categorización simple)
    ("clasificacion", "simple"): "claude-haiku-4-5",
    ("clasificacion", "medio"): "claude-haiku-4-5",
    ("clasificacion", "complejo"): "claude-haiku-4-5",
    # Extracción: haiku para simple, sonnet para medio/complejo
    ("extraccion_entidades", "simple"): "claude-haiku-4-5",
    ("extraccion_entidades", "medio"): "claude-sonnet-4-6",
    ("extraccion_entidades", "complejo"): "claude-sonnet-4-6",
    # Resumen: sonnet para simple/medio, opus solo para complejo
    ("resumen_ejecutivo", "simple"): "claude-sonnet-4-6",
    ("resumen_ejecutivo", "medio"): "claude-sonnet-4-6",
    ("resumen_ejecutivo", "complejo"): "claude-opus-4-6",
    # Recomendación: sonnet para simple, opus para medio/complejo
    ("recomendacion_accion", "simple"): "claude-sonnet-4-6",
    ("recomendacion_accion", "medio"): "claude-opus-4-6",
    ("recomendacion_accion", "complejo"): "claude-opus-4-6",
}
