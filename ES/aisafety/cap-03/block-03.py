# Extraido de: LibroAISafety/cap-03-dentro-del-modelo.md
# Presupuesto de tokens de seguridad para una ventana de contexto
# Ejemplo para un sistema con agentes y RAG

VENTANA_CONTEXTO = 200_000  # tokens disponibles

# Presupuesto de seguridad: mínimo 5% del contexto total
PRESUPUESTO_SEGURIDAD = int(VENTANA_CONTEXTO * 0.05)  # 10.000 tokens

DISTRIBUCION_SEGURIDAD = {
    "system_prompt_principal": 3_000,        # instrucciones base
    "system_prompt_sandwich": 1_500,         # repetición al final
    "prefijos_rag": 500,                     # antes de cada documento
    "sufijos_herramientas": 500,             # después de cada tool result
    "recordatorios_periodicos": 2_000,       # cada 20K tokens de historial
    "reserva_validacion": 2_500,             # para filtros dinámicos
}

# Tokens disponibles para contenido de usuario
TOKENS_CONTENIDO = VENTANA_CONTEXTO - PRESUPUESTO_SEGURIDAD
# 190.000 tokens para contenido real

def verificar_presupuesto(tokens_seguridad_usados: int) -> bool:
    """Verifica que el presupuesto de seguridad se mantiene.
    Si baja del 3%, emitir alerta."""
    ratio = tokens_seguridad_usados / VENTANA_CONTEXTO
    if ratio < 0.03:
        # Alerta: las instrucciones de seguridad están
        # infrarepresentadas en el contexto
        return False
    return True
