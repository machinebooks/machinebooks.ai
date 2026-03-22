# Extraído de: LibroConsultor/cap-02-anatomia-proyecto.md
import anthropic
from datetime import datetime

client = anthropic.Anthropic()

def extract_lessons_learned(
    project_name: str,
    deliverables_summary: str,
    deviations: list[str],
    team_feedback: list[str],
    client_feedback: str
) -> dict:
    """Extrae lecciones aprendidas de forma estructurada al cierre del proyecto."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Eres un analista de mejora continua en una práctica
de consultoría tecnológica. Tu trabajo: extraer lecciones aprendidas
de un proyecto completado, estructurarlas por categoría y generar
recomendaciones accionables para proyectos futuros.

Categorías de lecciones:
- ESTIMACION: desviaciones en esfuerzo, plazos o alcance
- METODOLOGIA: qué funcionó y qué no en el enfoque técnico
- CLIENTE: patrones de comunicación, expectativas, fricciones
- HERRAMIENTAS: eficacia de agentes, RAG, plantillas usadas
- EQUIPO: coordinación, onboarding, distribución de carga

Cada lección debe incluir: qué pasó, por qué importa,
qué hacer diferente la próxima vez. Máximo 3 frases por lección.""",
        messages=[{
            "role": "user",
            "content": f"""Proyecto: {project_name}
Fecha de cierre: {datetime.now().strftime('%Y-%m-%d')}

Resumen de entregables: {deliverables_summary}

Desviaciones respecto al plan:
{chr(10).join(f'- {d}' for d in deviations)}

Feedback del equipo:
{chr(10).join(f'- {f}' for f in team_feedback)}

Feedback del cliente: {client_feedback}

Genera las lecciones aprendidas en JSON:
{{
  "project": "nombre",
  "lessons": [
    {{
      "category": "ESTIMACION|METODOLOGIA|CLIENTE|HERRAMIENTAS|EQUIPO",
      "title": "título breve",
      "description": "qué pasó y por qué importa",
      "recommendation": "qué hacer diferente",
      "severity": "alta|media|baja"
    }}
  ],
  "metrics": {{
    "planned_hours": N,
    "actual_hours": N,
    "deviation_percentage": N,
    "client_satisfaction": "alta|media|baja"
  }}
}}"""
        }]
    )
    return json.loads(message.content[0].text)
