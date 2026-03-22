# Extraído de: LibroDevSecOps/cap-15-seguridad-agentes.md
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Any

class RiskLevel(Enum):
    """Clasificación de riesgo para herramientas de agente."""
    READ = "read"           # Lectura de datos, sin efecto secundario
    ANALYZE = "analyze"     # Ejecución de escaneos, consulta a APIs
    MODIFY = "modify"       # Creación de ramas, PRs, ficheros
    DESTRUCTIVE = "destruct"  # Merge, deploy, revocación, borrado

@dataclass
class SecureTool:
    """Envoltorio de herramienta con metadatos de seguridad."""
    name: str
    func: Callable
    risk_level: RiskLevel
    description: str
    max_calls_per_run: int = 50    # Límite de invocaciones por ejecución
    requires_approval: bool = False # Gate humano obligatorio
    allowed_args: dict = field(default_factory=dict)  # Restricción de argumentos

@dataclass
class AgentPermissions:
    """Perfil de permisos para un agente del pipeline."""
    agent_name: str
    allowed_risk_levels: list[RiskLevel]
    max_total_tool_calls: int = 100
    max_tokens_budget: int = 50_000
    max_execution_seconds: int = 300
    human_approval_channel: str = "slack://security-approvals"

# Perfiles predefinidos para agentes del pipeline
TRIAGE_AGENT_PERMS = AgentPermissions(
    agent_name="triage-agent",
    allowed_risk_levels=[RiskLevel.READ, RiskLevel.ANALYZE],
    max_total_tool_calls=200,
    max_tokens_budget=100_000,
    max_execution_seconds=600,
)

REMEDIATION_AGENT_PERMS = AgentPermissions(
    agent_name="remediation-agent",
    allowed_risk_levels=[RiskLevel.READ, RiskLevel.ANALYZE, RiskLevel.MODIFY],
    max_total_tool_calls=50,
    max_tokens_budget=80_000,
    max_execution_seconds=300,
)
