# Extraído de: LibroConsultor/cap-14-reporting.md
import anthropic

client = anthropic.Anthropic()

def generar_narrativa_hallazgo(
    hallazgo: Hallazgo,
    contexto_proyecto: str,
    voice_prompt: str
) -> str:
    """Genera la narrativa de un hallazgo individual."""

    prompt_usuario = f"""Redacta la narrativa para este hallazgo de consultoría.

HALLAZGO:
- Título: {hallazgo.titulo}
- Descripción técnica: {hallazgo.descripcion}
- Evidencia: {hallazgo.evidencia}
- Severidad: {hallazgo.severidad.value}
- Área: {hallazgo.area}
- Impacto en negocio: {hallazgo.impacto_negocio}

CONTEXTO DEL PROYECTO:
{contexto_proyecto}

INSTRUCCIONES:
1. Redacta 2-4 párrafos que narren el hallazgo.
2. Abre con el hecho observado, no con la recomendación.
3. Conecta con impacto de negocio en el segundo párrafo.
4. Si hay datos cuantitativos en la evidencia, inclúyelos.
5. Cierra con la implicación, no con la solución
   (la solución va en Recomendaciones).
6. Extensión: 150-250 palabras."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=voice_prompt,
        messages=[{"role": "user", "content": prompt_usuario}]
    )
    return response.content[0].text
