# Extraido de: LibroAISafety/cap-23-programa-safety.md
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"          # chatbot interno, sin datos sensibles
    MEDIUM = "medium"    # asistente con acceso a datos de negocio
    HIGH = "high"        # agente autónomo con acceso a datos de clientes
    CRITICAL = "critical" # agente con capacidad de acción financiera

@dataclass
class AISystemInventory:
    """Registro de cada sistema de IA en la organización."""
    system_id: str
    name: str
    description: str
    model_provider: str       # Anthropic, OpenAI, Azure OpenAI, local
    model_name: str           # claude-sonnet-4-6, gpt-4o, llama-3.1
    deployment_date: date
    owner_team: str
    risk_level: RiskLevel
    has_tool_use: bool = False
    has_rag: bool = False
    has_autonomous_actions: bool = False
    security_review_date: date | None = None
    guardrails_implemented: list[str] = field(default_factory=list)
    known_risks: list[str] = field(default_factory=list)
    last_red_team_date: date | None = None

# Ejemplo: inventario de tres sistemas
inventory = [
    AISystemInventory(
        system_id="AI-001",
        name="Asistente de RRHH",
        description="Chatbot para consultas de nóminas y vacaciones",
        model_provider="Anthropic",
        model_name="claude-haiku-4-5",
        deployment_date=date(2025, 9, 15),
        owner_team="RRHH",
        risk_level=RiskLevel.MEDIUM,
        has_tool_use=False,
        has_rag=True,
        guardrails_implemented=["input_filter", "pii_detector"],
        known_risks=["PII en respuestas", "inyección vía docs RAG"],
    ),
    AISystemInventory(
        system_id="AI-002",
        name="Agente de análisis financiero",
        description="Agente autónomo que consulta y analiza datos de coste",
        model_provider="Anthropic",
        model_name="claude-sonnet-4-6",
        deployment_date=date(2026, 1, 10),
        owner_team="Finanzas",
        risk_level=RiskLevel.CRITICAL,
        has_tool_use=True,
        has_rag=True,
        has_autonomous_actions=True,
        guardrails_implemented=["input_filter", "tool_validator", "output_filter"],
        known_risks=["Escalada de privilegios vía tool use", "Cross-tenant data"],
    ),
]
