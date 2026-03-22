# Extraído de: LibroDevSecOps/cap-06-secretos.md
from claude_agent_sdk import Agent, tool

@tool
def classify_leaked_secret(
    secret_type: str,
    service: str,
    environment: str
) -> dict:
    """Clasifica un secreto filtrado por impacto y urgencia de rotación."""
    # Matriz de impacto según tipo y entorno
    impact_matrix = {
        ("aws-access-key", "production"): "critical",
        ("aws-access-key", "staging"): "high",
        ("database-password", "production"): "critical",
        ("database-password", "development"): "medium",
        ("api-key-readonly", "production"): "medium",
        ("api-key-readonly", "development"): "low",
    }
    impact = impact_matrix.get(
        (secret_type, environment), "high"  # Por defecto, asumir alto
    )
    return {
        "impact": impact,
        "rotate_within": {
            "critical": "1 hora",
            "high": "4 horas",
            "medium": "24 horas",
            "low": "7 días",
        }[impact],
        "notify": ["security-team"] if impact in ("critical", "high")
                  else ["dev-team"],
    }
