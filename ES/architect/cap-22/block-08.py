# Extraído de: LibroTecnico/cap-22-observabilidad.md
@dataclass
class AgentTrace:
    """Traza completa de una ejecución agentic."""
    session_id: str
    agent_slug: str
    user_id: int
    started_at: float
    steps: List[TraceStep] = field(default_factory=list)

    def add_step(self, step_type: str, data: dict, duration_ms: float):
        self.steps.append(TraceStep(
            step_type=step_type,  # "llm_call", "tool_exec", "guardrail_check"
            data=data,
            duration_ms=duration_ms,
            timestamp=time.time()
        ))

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "agent_slug": self.agent_slug,
            "total_steps": len(self.steps),
            "total_duration_ms": sum(s.duration_ms for s in self.steps),
            "llm_calls": len([s for s in self.steps if s.step_type == "llm_call"]),
            "tool_executions": len([s for s in self.steps if s.step_type == "tool_exec"]),
            "guardrail_triggers": len([s for s in self.steps if s.step_type == "guardrail_check"]),
            "steps": [s.to_dict() for s in self.steps]
        }
