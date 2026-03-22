# Extraído de: LibroDevSecOps/cap-15-seguridad-agentes.md
import uuid
import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("agent.audit")

@dataclass
class SecurityContext:
    """Contexto de seguridad para cada acción de agente."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    agent_run_id: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    action: str = ""              # Nombre de la herramienta invocada
    risk_level: str = ""          # read / analyze / modify / destruct
    args_sanitized: dict = field(default_factory=dict)
    result_summary: str = ""      # Resumen del resultado (no el resultado completo)
    outcome: str = ""             # success / failure / rejected / budget_exceeded
    approved_by: str | None = None  # ID del humano que aprobó, si aplica
    tokens_consumed: int = 0
    execution_ms: int = 0

class AgentAuditMiddleware:
    """Middleware que registra cada acción con SecurityContext."""

    def __init__(self, agent_name: str, run_id: str):
        self.agent_name = agent_name
        self.run_id = run_id
        self.contexts: list[SecurityContext] = []

    def log_action(
        self,
        tool: SecureTool,
        args: dict,
        result: Any,
        outcome: str,
        approved_by: str | None = None,
        tokens: int = 0,
        duration_ms: int = 0,
    ) -> SecurityContext:
        """Crea y persiste un SecurityContext para la acción."""
        ctx = SecurityContext(
            agent_name=self.agent_name,
            agent_run_id=self.run_id,
            action=tool.name,
            risk_level=tool.risk_level.value,
            args_sanitized=_sanitize_args(args),
            result_summary=_summarize_result(result),
            outcome=outcome,
            approved_by=approved_by,
            tokens_consumed=tokens,
            execution_ms=duration_ms,
        )
        self.contexts.append(ctx)

        # Registro estructurado para SIEM / Elasticsearch / Loki
        logger.info(
            json.dumps(asdict(ctx), ensure_ascii=False)
        )
        return ctx

    def get_run_summary(self) -> dict:
        """Genera resumen de la ejecución completa del agente."""
        return {
            "agent": self.agent_name,
            "run_id": self.run_id,
            "total_actions": len(self.contexts),
            "outcomes": _count_outcomes(self.contexts),
            "risk_distribution": _count_risk_levels(self.contexts),
            "total_tokens": sum(c.tokens_consumed for c in self.contexts),
            "approvals_required": sum(
                1 for c in self.contexts if c.approved_by
            ),
        }

def _summarize_result(result: Any) -> str:
    """Resumen seguro del resultado, sin datos sensibles."""
    if isinstance(result, dict):
        return json.dumps(
            {k: type(v).__name__ for k, v in result.items()}
        )
    return str(result)[:200]

def _count_outcomes(contexts: list[SecurityContext]) -> dict:
    counts: dict[str, int] = {}
    for ctx in contexts:
        counts[ctx.outcome] = counts.get(ctx.outcome, 0) + 1
    return counts

def _count_risk_levels(contexts: list[SecurityContext]) -> dict:
    counts: dict[str, int] = {}
    for ctx in contexts:
        counts[ctx.risk_level] = counts.get(ctx.risk_level, 0) + 1
    return counts
