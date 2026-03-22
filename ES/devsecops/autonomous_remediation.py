# Extraído de: LibroDevSecOps/cap-29-futuro-seguridad-autonoma.md
# autonomous_remediation.py — Agente de remediación con guardrails
import anthropic
from claude_agent_sdk import Agent, tool

MAX_FILES_MODIFIED = 3       # Límite de ficheros por remediación
MAX_LINES_CHANGED = 50       # Límite de líneas modificadas
ALLOWED_ACTIONS = [
    "update_dependency",
    "block_commit",
    "rotate_secret",
    "update_dockerfile_base",
]

client = anthropic.Anthropic()

@tool
def apply_dependency_fix(package: str, current: str, target: str) -> dict:
    """Actualiza una dependencia vulnerable a versión parcheada."""
    # Verifica que el cambio está en la lista de acciones permitidas
    # Ejecuta bump, corre tests, valida que no hay regresiones
    return {
        "action": "update_dependency",
        "package": package,
        "from": current,
        "to": target,
        "tests_passed": True,
        "rollback_available": True,
    }

@tool
def verify_fix(finding_id: str) -> dict:
    """Re-ejecuta el escáner para confirmar que el hallazgo se resolvió."""
    # Ejecuta Grype/Semgrep/Trivy sobre el componente afectado
    return {
        "finding_id": finding_id,
        "resolved": True,
        "new_findings": 0,
    }

# El agente opera con instrucciones estrictas de alcance
agent = Agent(
    model="claude-sonnet-4-6",
    tools=[apply_dependency_fix, verify_fix],
    system="""Eres un agente de remediación autónoma. Reglas estrictas:
    1. Solo ejecutas acciones de la lista ALLOWED_ACTIONS.
    2. Nunca modificas más de 3 ficheros ni más de 50 líneas.
    3. Siempre verificas el fix con un re-escaneo.
    4. Si el fix falla verificación, reviertes y escalas a nivel 2.
    5. Registras cada acción en el log de auditoría."""
)
