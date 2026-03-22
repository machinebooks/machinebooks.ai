# Extraído de: LibroConsultor/cap-28-caso-sector-publico.md
from anthropic import Anthropic
import json

client = Anthropic()

SYSTEM_PROMPT = """Eres un agente de evaluación de madurez de IA especializado
en administración pública española. Tu tarea es analizar documentos internos
de un organismo público y evaluar su nivel de madurez en cada dimensión.

Contexto regulatorio aplicable:
- Esquema Nacional de Seguridad (ENS) - RD 311/2022
- Reglamento de IA de la UE (AI Act) - Reglamento 2024/1689
- RGPD y LOPDGDD
- Ley 40/2015 de Régimen Jurídico del Sector Público

Para cada documento analizado, extrae:
1. Dimensión(es) de madurez afectada(s)
2. Nivel estimado (1-5) con justificación
3. Evidencias textuales que soportan la evaluación
4. Gaps identificados respecto al nivel objetivo
5. Restricciones regulatorias que afectan a la dimensión

IMPORTANTE: Si no encuentras evidencia suficiente, indica nivel 1 con
nota 'evidencia insuficiente'. No asumas capacidades no documentadas.
Sé conservador en la evaluación — en sector público, sobrevalorar
la madurez genera roadmaps inviables."""

def evaluar_documento(contenido_documento: str, metadata: dict) -> dict:
    """Evalúa un documento del organismo contra el framework de madurez."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Analiza el siguiente documento del organismo:

Tipo: {metadata['tipo']}
Fecha: {metadata['fecha']}
Área: {metadata['area']}

CONTENIDO:
{contenido_documento}

Genera la evaluación de madurez estructurada en JSON."""
        }]
    )
    return json.loads(response.content[0].text)
