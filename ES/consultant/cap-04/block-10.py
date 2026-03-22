# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
LESSON_SCHEMA = {
    "proyecto_tipo": str,      # auditoría, consultoría, assessment
    "sector": str,             # público, financiero, industrial
    "fase": str,               # alcance, ejecución, entrega, cierre
    "problema": str,           # qué salió mal o qué se aprendió
    "causa_raiz": str,         # por qué ocurrió
    "accion_correctiva": str,  # qué se hizo
    "recomendacion": str,      # qué hacer en el futuro
    "impacto": str,            # alto, medio, bajo
    "fecha": str               # YYYY-MM
}
