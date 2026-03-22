# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: análisis de documento con Claude
# Patrón: ai_service/tasks/document_analysis.py

import anthropic

client = anthropic.Anthropic()

def analyze_requirements_document(
    document_text: str,
    analysis_config: dict
) -> dict:
    """
    Analiza un documento de requisitos usando claude-opus-4-6.
    Produce resumen ejecutivo, requisitos clave y recomendación GO/NO-GO.
    """
    system_prompt = f"""
    Eres un analista técnico experto en evaluación de oportunidades de negocio.
    Tu tarea es analizar el siguiente documento de requisitos y producir:
    1. Resumen ejecutivo (máximo 300 palabras)
    2. Lista de requisitos clave con ponderación (1-5) y tipo (técnico/administrativo/económico)
    3. Cláusulas de riesgo identificadas
    4. Recomendación GO/NO-GO con justificación basada en:
       - Alineación con capacidades declaradas: {analysis_config.get('capabilities', [])}
       - Umbrales de solvencia configurados: {analysis_config.get('thresholds', {})}

    Responde EXCLUSIVAMENTE en formato JSON con la estructura definida.
    Si no encuentras información suficiente para un campo, indica "INSUFICIENTE".
    """

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"Analiza el siguiente documento:\n\n{document_text}"
            }
        ],
        system=system_prompt
    )

    # El resultado se persiste en Document.ai_analysis (JSON)
    return parse_analysis_response(response.content[0].text)
