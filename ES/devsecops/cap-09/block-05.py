# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
from claude_agent_sdk import tool

@tool
def estimate_fix_complexity(
    finding_source: str,
    finding_title: str,
    fixed_version: str | None,
    code_snippet: str | None,
    file_path: str | None
) -> dict:
    """Estima el esfuerzo de corrección: trivial, bajo,
    medio o alto. Incluye tipo de fix recomendado."""
    complexity = "medium"
    fix_type = "manual_review"
    estimated_hours = 4.0
    breaking_change_risk = False

    # SCA: si hay versión fija, es actualización de dependencia
    if finding_source == "sca" and fixed_version:
        # Verificar si es major version bump
        if fixed_version and code_snippet:
            complexity = "low"
            fix_type = "dependency_update"
            estimated_hours = 0.5
        else:
            complexity = "low"
            fix_type = "dependency_update"
            estimated_hours = 0.5

    # Container: actualización de imagen base
    elif finding_source == "container":
        if "base image" in finding_title.lower():
            complexity = "low"
            fix_type = "base_image_update"
            estimated_hours = 1.0
        else:
            complexity = "medium"
            fix_type = "dockerfile_modification"
            estimated_hours = 2.0

    # SAST: depende del tipo de vulnerabilidad
    elif finding_source == "sast":
        sast_simple = ["hardcoded-secret", "missing-header",
                       "insecure-cookie", "debug-enabled"]
        sast_medium = ["sql-injection", "xss", "path-traversal",
                       "open-redirect", "ssrf"]
        title_lower = finding_title.lower()
        if any(p in title_lower for p in sast_simple):
            complexity = "trivial"
            fix_type = "config_change"
            estimated_hours = 0.25
        elif any(p in title_lower for p in sast_medium):
            complexity = "medium"
            fix_type = "code_refactor"
            estimated_hours = 4.0
        else:
            complexity = "high"
            fix_type = "architectural_change"
            estimated_hours = 8.0

    return {
        "complexity": complexity,
        "fix_type": fix_type,
        "estimated_hours": estimated_hours,
        "breaking_change_risk": breaking_change_risk,
    }
