# Extraído de: LibroDevSecOps/cap-04-sast-inteligente.md
def triaje_escalonado(hallazgos: list[dict]) -> list[dict]:
    """Pipeline de triaje en dos fases: Haiku filtra, Sonnet analiza."""
    resultados = []

    # Fase 1: clasificación rápida con Haiku
    for h in hallazgos:
        contexto = leer_codigo_circundante(h["path"], h["start"]["line"])
        respuesta = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""Clasifica este hallazgo SAST como
"probable_verdadero" o "probable_falso". Solo responde con JSON:
{{"clasificacion": "...", "motivo": "..."}}

Regla: {h["check_id"]}
Código:\n