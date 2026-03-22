# Extraído de: LibroConsultor/cap-03-consultor-potenciado.md
ESTIMATION_SYSTEM_PROMPT = """Eres un estimador de proyectos de consultoría
tecnológica con acceso a datos históricos de proyectos completados.

Tu trabajo: dado un nuevo proyecto, buscar los proyectos más similares
en la base histórica, analizar sus métricas reales (esfuerzo, duración,
equipo, desviación) y generar una estimación calibrada.

Reglas de estimación:
- Nunca des un número único. Da un rango con tres escenarios:
  optimista (P25), probable (P50), pesimista (P75).
- Incluye el factor de complejidad regulatoria (1.0 a 2.5).
- Incluye el factor de madurez del cliente (1.0 a 1.8):
  cliente con buena documentación = 1.0, cliente sin procesos = 1.8.
- Lista los supuestos que condicionan la estimación.
- Lista los riesgos que podrían mover la estimación al escenario pesimista.
- Muestra los proyectos históricos usados como referencia.

IMPORTANTE: si hay menos de 3 proyectos comparables en la base,
adviértelo explícitamente. Una estimación sin base histórica
es una opinión, no una estimación."""

def estimate_project(
    description: str,
    historical_projects: list[dict]
) -> dict:
    """Genera estimación calibrada basada en históricos."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=ESTIMATION_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Estima este proyecto:

{description}

Proyectos históricos comparables:
{json.dumps(historical_projects, indent=2, ensure_ascii=False)}

Responde en JSON:
{{
  "estimation": {{
    "optimistic_hours": N,
    "probable_hours": N,
    "pessimistic_hours": N,
    "team_size_recommended": N,
    "duration_weeks": {{
      "optimistic": N,
      "probable": N,
      "pessimistic": N
    }}
  }},
  "complexity_factors": {{
    "regulatory": N,
    "client_maturity": N,
    "technical": N
  }},
  "comparable_projects": [
    {{
      "name": "referencia anonimizada",
      "similarity_score": 0.0-1.0,
      "actual_hours": N,
      "deviation_from_estimate": "N%"
    }}
  ],
  "assumptions": ["..."],
  "risks": ["..."],
  "confidence": "alta|media|baja",
  "confidence_justification": "..."
}}"""
        }]
    )
    return json.loads(message.content[0].text)
