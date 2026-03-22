# Extraído de: LibroConsultor/cap-14-reporting.md
def generar_especificacion_grafico(
    datos: dict,
    tipo_grafico: str,
    contexto: str,
    voice_prompt: str
) -> dict:
    """Genera especificación de gráfico + texto descriptivo."""

    prompt = f"""Genera la especificación para un gráfico de
informe de consultoría.

DATOS:
{datos}

TIPO DE GRÁFICO SUGERIDO: {tipo_grafico}
CONTEXTO: {contexto}

Genera un JSON con:
1. "tipo": tipo de gráfico óptimo para estos datos.
2. "titulo": título del gráfico (max 10 palabras).
3. "ejes": descripción de ejes X e Y.
4. "colores": paleta sugerida (max 5 colores hex).
5. "texto_alternativo": descripción en prosa del gráfico
   (para accesibilidad y para el informe Word).
6. "insight_principal": la conclusión que el lector debe
   extraer del gráfico (1 frase).
7. "datos_chart": datos formateados para Matplotlib/Recharts."""

    response = client.messages.create(
        model="claude-haiku-4-5",  # Haiku para estructura simple
        max_tokens=2048,
        system=voice_prompt,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    return json.loads(response.content[0].text)
