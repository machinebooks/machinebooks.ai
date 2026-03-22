# Extraído de: LibroFinOps/cap-09-cache-prompt-batch.md
# Ejemplo: extracción de campos de un documento de licitación
EXTRACTION_PROMPT_VERBOSE = """
Por favor, analiza el siguiente texto del documento de licitación
y proporciona los campos más relevantes que puedas identificar,
incluyendo el título, el presupuesto base, la fecha límite
y si se requiere acreditación de solvencia económica.

Texto del documento:
{document_text}
"""
# Tokens de salida típicos: ~180 tokens (texto explicativo + datos)

EXTRACTION_PROMPT_JSON = """Extrae del siguiente texto los campos indicados.
Responde ÚNICAMENTE con JSON válido, sin texto adicional.

Esquema esperado:
{{
  "titulo": "string",
  "presupuesto_base": number,
  "fecha_limite": "YYYY-MM-DD",
  "requiere_solvencia": boolean
}}

Texto:
{document_text}"""
# Tokens de salida típicos: ~45 tokens (solo el JSON)

def extract_fields(document_text: str, middleware: CachingMiddleware) -> dict:
    """
    Extrae campos estructurados con JSON mode.
    Reduccion de tokens de salida: ~75 % respecto al prompt verboso.
    """
    import json

    response = middleware.create_with_cache(
        model="claude-haiku-4-5",  # extraccion = tarea nivel FAST
        system="Eres un extractor de datos estructurados. Responde solo con JSON.",
        user_message=EXTRACTION_PROMPT_JSON.format(document_text=document_text),
        max_tokens=256,  # limite ajustado al output esperado
    )

    text = response.content[0].text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: reintentar con instrucción más explícita
        # En produccion, registrar el fallo para analisis
        return {}
