# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
# Ejemplo didáctico: patrones/chat/context_budget.py
# Presupuesto de tokens por capa de contexto

TOKEN_BUDGET = {
    "system_prompt": 800,        # Instrucciones base — nunca se truncan
    "user_memories": 600,        # Top 10 memorias por relevancia
    "rag_context": 4_000,        # Chunks recuperados de Qdrant
    "conversation_history": 6_000,  # Historial de la sesión
    "reserved_for_response": 2_000,  # Espacio para la respuesta de Claude
}
# Total: ~13.400 tokens de un límite de ~200K
# En la práctica el límite real depende del modelo:
# Haiku: 200K, Sonnet: 200K, Opus: 200K

MAX_CONTEXT = 180_000  # Margen de seguridad del 10%
