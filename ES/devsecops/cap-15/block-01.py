# Extraído de: LibroDevSecOps/cap-15-seguridad-agentes.md
import time
from dataclasses import dataclass, field

@dataclass
class BudgetState:
    """Estado acumulado de consumo del agente."""
    tool_calls: int = 0
    tokens_used: int = 0
    start_time: float = field(default_factory=time.time)
    actions_log: list = field(default_factory=list)

class BudgetExceeded(Exception):
    """El agente ha superado su presupuesto asignado."""
    def __init__(self, dimension: str, limit: int, actual: int):
        self.dimension = dimension
        self.limit = limit
        self.actual = actual
        super().__init__(
            f"Presupuesto excedido: {dimension} "
            f"(límite={limit}, actual={actual})"
        )

class AgentBudgetGuard:
    """Circuit breaker que detiene al agente al superar límites."""

    def __init__(self, permissions: AgentPermissions):
        self.permissions = permissions
        self.state = BudgetState()

    def check_budget(self) -> None:
        """Verifica presupuesto antes de cada invocación."""
        elapsed = time.time() - self.state.start_time

        if self.state.tool_calls >= self.permissions.max_total_tool_calls:
            raise BudgetExceeded(
                "tool_calls",
                self.permissions.max_total_tool_calls,
                self.state.tool_calls,
            )
        if self.state.tokens_used >= self.permissions.max_tokens_budget:
            raise BudgetExceeded(
                "tokens",
                self.permissions.max_tokens_budget,
                self.state.tokens_used,
            )
        if elapsed >= self.permissions.max_execution_seconds:
            raise BudgetExceeded(
                "execution_seconds",
                self.permissions.max_execution_seconds,
                int(elapsed),
            )

    def record_call(self, tool_name: str, tokens: int, args: dict):
        """Registra cada invocación para auditoría y control."""
        self.state.tool_calls += 1
        self.state.tokens_used += tokens
        self.state.actions_log.append({
            "tool": tool_name,
            "tokens": tokens,
            "args_summary": _sanitize_args(args),
            "timestamp": time.time(),
            "cumulative_calls": self.state.tool_calls,
        })

def _sanitize_args(args: dict) -> dict:
    """Elimina valores sensibles antes de registrar."""
    sensitive_keys = {"api_key", "token", "password", "secret"}
    return {
        k: "***REDACTED***" if k in sensitive_keys else v
        for k, v in args.items()
    }
