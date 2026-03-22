# Extraído de: LibroDevSecOps/cap-25-madurez-devsecops.md
# roadmap_agent.py — Generación de roadmap de madurez con Claude
import anthropic
import json

client = anthropic.Anthropic()

ROADMAP_SYSTEM_PROMPT = """Eres un consultor DevSecOps que genera roadmaps de mejora
de madurez. Recibes el estado actual (niveles por dominio), el objetivo y las restricciones.

Genera un roadmap en JSON con esta estructura:
{
  "phases": [
    {
      "name": "Fase 1 — Fundamentos",
      "duration_months": 3,
      "objectives": ["descripción"],
      "actions": [
        {"domain": "PS", "from_level": 1, "to_level": 2,
         "action": "qué hacer", "effort": "S/M/L",
         "prerequisite": null, "kpi": "métrica de éxito"}
      ],
      "expected_score_delta": 0.5
    }
  ],
  "critical_path": ["acción que bloquea otras"],
  "risks": ["riesgo del plan"],
  "total_months": 12
}

Reglas:
1. Nunca proponer saltar más de un nivel en un trimestre por dominio.
2. Priorizar dominios con nivel 0-1 sobre mejoras de nivel 3-4.
3. Las acciones deben ser concretas: "implementar Semgrep en CI", no "mejorar seguridad".
4. Cada acción debe tener un KPI medible.
5. El esfuerzo (S/M/L) considera equipo de 2-3 personas dedicadas a seguridad.
"""

def generate_roadmap(
    current_levels: dict[str, int],
    target_levels: dict[str, int],
    constraints: dict,
) -> dict:
    """Genera roadmap de progresión de madurez."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=ROADMAP_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Estado actual por dominio: {json.dumps(current_levels)}
Objetivo a 12 meses: {json.dumps(target_levels)}
Restricciones: {json.dumps(constraints)}

Genera el roadmap de progresión."""
        }]
    )
    return json.loads(message.content[0].text)

# Ejemplo de invocación
roadmap = generate_roadmap(
    current_levels={"PS": 2, "VM": 1, "GOV": 1, "MR": 1, "AIS": 0, "CA": 1},
    target_levels={"PS": 3, "VM": 3, "GOV": 2, "MR": 2, "AIS": 2, "CA": 2},
    constraints={
        "team_size": 3,
        "budget_eur_annual": 80000,
        "regulation": ["ENS nivel medio", "AI Act"],
        "ai_in_production": True,
        "current_tools": ["Semgrep", "Grype", "Trivy", "Gitleaks"],
    }
)
