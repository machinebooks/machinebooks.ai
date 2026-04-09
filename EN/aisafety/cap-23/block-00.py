# Extracted from: LibroAISafety/ch-23-safety-program.md
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"          # internal chatbot, no sensitive data
    MEDIUM = "medium"    # assistant with access to business data
    HIGH = "high"        # autonomous agent with access to customer data
    CRITICAL = "critical" # agent with financial action capability

@dataclass
class AISystemInventory:
    """Record of each AI system in the organization."""
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

# Example: inventory of three systems
inventory = [
    AISystemInventory(
        system_id="AI-001",
        name="HR Assistant",
        description="Chatbot for payroll and vacation queries",
        model_provider="Anthropic",
        model_name="claude-haiku-4-5",
        deployment_date=date(2025, 9, 15),
        owner_team="HR",
        risk_level=RiskLevel.MEDIUM,
        has_tool_use=False,
        has_rag=True,
        guardrails_implemented=["input_filter", "pii_detector"],
        known_risks=["PII in responses", "injection via RAG docs"],
    ),
    AISystemInventory(
        system_id="AI-002",
        name="Financial analysis agent",
        description="Autonomous agent that queries and analyzes cost data",
        model_provider="Anthropic",
        model_name="claude-sonnet-4-6",
        deployment_date=date(2026, 1, 10),
        owner_team="Finance",
        risk_level=RiskLevel.CRITICAL,
        has_tool_use=True,
        has_rag=True,
        has_autonomous_actions=True,
        guardrails_implemented=["input_filter", "tool_validator", "output_filter"],
        known_risks=["Privilege escalation via tool use", "Cross-tenant data"],
    ),
]
