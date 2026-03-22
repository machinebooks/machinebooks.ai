# Extraído de: LibroConsultor/cap-14-reporting.md
def extraer_correcciones_voz(
    borrador_original: str,
    texto_corregido: str,
    voice_prompt: str
) -> str:
    """Analiza correcciones para actualizar el voice prompt."""

    prompt = f"""Compara el borrador original con la versión corregida
por el consultor senior. Identifica patrones de corrección
que indiquen ajustes necesarios en el prompt de voz.

BORRADOR ORIGINAL:
{borrador_original[:3000]}

VERSIÓN CORREGIDA:
{texto_corregido[:3000]}

VOICE PROMPT ACTUAL:
{voice_prompt}

Genera:
1. Lista de patrones de corrección (qué se cambió
   sistemáticamente).
2. Reglas nuevas para añadir al voice prompt.
3. Reglas existentes que necesitan refinarse.
4. Voice prompt actualizado completo."""

    response = client.messages.create(
        model="claude-opus-4-6",  # Opus para análisis de estilo
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
