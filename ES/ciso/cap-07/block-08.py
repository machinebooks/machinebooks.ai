# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
# Ejemplo de flujo del RiskAgent con Claude Agent SDK
# El agente recibe la consulta, identifica la intención y usa herramientas

import anthropic

client = anthropic.Anthropic()

# Herramientas registradas en el agente
tools = [
    {
        "name": "calculate_risk_matrix",
        "description": (
            "Calcula la matriz de riesgo para un análisis. "
            "Devuelve escenarios priorizados por nivel de riesgo, "
            "incluyendo los de riesgo alto sin plan de tratamiento."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "analysis_id": {
                    "type": "integer",
                    "description": "ID del análisis de riesgos"
                },
                "methodology": {
                    "type": "string",
                    "description": "Metodología activa"
                },
                "filters": {
                    "type": "object",
                    "description": "Filtros: risk_level, asset_type, status"
                }
            },
            "required": ["analysis_id", "methodology"]
        }
    },
    {
        "name": "get_treatment_recommendations",
        "description": (
            "Genera recomendaciones de controles para un escenario "
            "de riesgo, basándose en el catálogo de amenazas de la "
            "metodología y buenas prácticas de seguridad."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "scenario_id": {"type": "integer"},
                "methodology": {"type": "string"}
            },
            "required": ["scenario_id"]
        }
    }
]

# El agente procesa la consulta del CISO
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    system=(
        "Eres el agente de riesgos de una plataforma GRC. "
        "Consulta los datos del análisis antes de responder. "
        "Presenta los riesgos ordenados por criticidad. "
        "Para cada riesgo alto sin tratamiento, sugiere una estrategia."
    ),
    tools=tools,
    messages=[{
        "role": "user",
        "content": (
            "¿Cuáles son los riesgos altos sin plan de tratamiento "
            "del análisis de este trimestre?"
        )
    }]
)

# El agente invoca calculate_risk_matrix con filtro risk_level="alto"
# y devuelve la lista priorizada al CISO en lenguaje natural
