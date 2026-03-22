# Extraído de: LibroConsultor/cap-02-anatomia-proyecto.md
import anthropic
import json

client = anthropic.Anthropic()

SYSTEM_PROMPT = """Eres un analista de operaciones de consultoría tecnológica.
Tu trabajo: dado un proyecto de consultoría, descomponer sus actividades
por fase (preventa, entrega, captura de conocimiento) y evaluar el potencial
de automatización con IA de cada actividad.

Criterios de evaluación:
- ALTO: tarea repetitiva, estructurada, con poca variabilidad entre proyectos.
  Ejemplos: búsqueda en normativa, generación de matrices, redacción de borradores.
- MEDIO: tarea con componente estructurado y componente de juicio.
  Ejemplos: análisis de gaps (la evaluación mecánica es automatizable,
  la priorización requiere contexto del cliente).
- BAJO: tarea donde el valor está en la interacción humana o el criterio experto.
  Ejemplos: reuniones con stakeholders, negociación de alcance, recomendaciones estratégicas.
- NINGUNO: tarea inherentemente humana.
  Ejemplos: construcción de confianza, lectura de dinámicas políticas del cliente.

Para cada actividad, estima horas manuales y horas con asistencia de IA.
Sé realista: la IA no elimina tareas, las acelera. El consultor siempre revisa.

Devuelve JSON válido con la estructura de actividades por fase."""

def analyze_project(project_description: str) -> dict:
    """Analiza un proyecto y genera el mapa de automatización."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Analiza este proyecto de consultoría y genera
el desglose de actividades con potencial de automatización:

{project_description}

Responde SOLO con JSON válido. Estructura esperada:
{{
  "project_summary": "...",
  "phases": {{
    "preventa": [
      {{
        "activity": "nombre",
        "hours_manual": N,
        "hours_assisted": N,
        "automation_potential": "alto|medio|bajo|ninguno",
        "requires_client_interaction": true|false,
        "requires_expert_judgment": true|false,
        "justification": "por qué esta evaluación"
      }}
    ],
    "entrega": [...],
    "captura_conocimiento": [...]
  }},
  "total_hours_manual": N,
  "total_hours_assisted": N,
  "reduction_percentage": N,
  "recommendations": ["...", "..."],
  "warnings": ["actividades que NO se deben automatizar y por qué"]
}}"""
        }]
    )
    return json.loads(message.content[0].text)
