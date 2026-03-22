# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Few-shot para clasificación de intención
# Los ejemplos proceden de interacciones reales anonimizadas

FEW_SHOT_EXAMPLES = """
EJEMPLO 1:
Mensaje: "¿Cuántas propuestas ganamos el trimestre pasado?"
Respuesta: {"intent": "CHAT_RAG", "confidence": 0.95, "reasoning": "Consulta informativa sobre datos históricos"}

EJEMPLO 2:
Mensaje: "Genera una propuesta competitiva para el cliente Acme"
Respuesta: {"intent": "WORKFLOW", "confidence": 0.92, "reasoning": "Proceso de generación multi-paso que requiere orquestación"}

EJEMPLO 3:
Mensaje: "Evalúa esta oportunidad y prepara la propuesta si es viable"
Respuesta: {"intent": "WORKFLOW", "confidence": 0.88, "reasoning": "Proceso multi-paso: evaluación + generación condicional"}
"""
