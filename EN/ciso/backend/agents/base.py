# Chapter 12 — BaseAgent: the contract every agent must fulfill
#
# Imposes a 3-phase lifecycle (gather -> analyze -> generate) with
# automatic tracing per phase. The execute() method is NOT overridable:
# child agents implement the three phases, but the flow and tracing
# are controlled by the base class. An auditor reviewing PrivacyAgent
# traces reads the exact same format as RiskAgent traces.

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
import time


class BaseAgent(ABC):
    """Abstract base for all GRC agents.

    Enforces:
    - 3-phase lifecycle (gather_data, analyze, generate_output)
    - Automatic tracing per phase (timestamps, tokens, cost)
    - Persistence of results and traces in the database

    Usage:
        agent = PrivacyAgent("privacy", llm_service, db_session)
        result = agent.execute(task_id="T-001", params={"processing_id": 42})
        print(result["traces"])  # Full audit trail
        print(f"Total cost: {result['total_cost']} EUR")
    """

    def __init__(self, agent_name: str, llm_service, db_session):
        self.agent_name = agent_name
        self.llm_service = llm_service
        self.db_session = db_session
        self.traces: list[dict] = []
        self.total_tokens: int = 0
        self.total_cost: float = 0.0

    def execute(self, task_id: str, params: dict) -> dict:
        """Execute the full lifecycle with automatic tracing.

        This method is NOT meant to be overridden. Child agents
        implement gather_data, analyze, and generate_output.
        """
        result: dict[str, Any] = {"task_id": task_id, "agent": self.agent_name}

        try:
            # Phase 1: Gather data from DB and RAG
            gathered = self._traced_phase(
                "gather_data", task_id,
                lambda: self.gather_data(params),
            )

            # Phase 2: Analyze with LLM
            analysis = self._traced_phase(
                "analyze", task_id,
                lambda: self.analyze(gathered, params),
            )

            # Phase 3: Generate output artifact
            output = self._traced_phase(
                "generate_output", task_id,
                lambda: self.generate_output(analysis, params),
            )

            result["status"] = "completed"
            result["output"] = output
            result["traces"] = self.traces
            result["total_tokens"] = self.total_tokens
            result["total_cost"] = round(self.total_cost, 6)

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self._record_trace(task_id, "error", {
                "exception": type(e).__name__,
                "message": str(e),
            })

        # Persist result and traces in the database
        self._persist_result(task_id, result)
        return result

    def _traced_phase(self, phase_name: str, task_id: str, fn: callable) -> Any:
        """Wrap a phase in automatic tracing."""
        start = time.monotonic()
        tokens_before = self.total_tokens

        result = fn()

        duration_ms = int((time.monotonic() - start) * 1000)
        tokens_used = self.total_tokens - tokens_before

        self._record_trace(task_id, phase_name, {
            "duration_ms": duration_ms,
            "tokens_used": tokens_used,
            "result_summary": self._summarize(result),
        })

        return result

    def _record_trace(self, task_id: str, phase: str, data: dict) -> None:
        """Record a tracing entry."""
        trace = {
            "task_id": task_id,
            "agent": self.agent_name,
            "phase": phase,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self.traces.append(trace)

    @abstractmethod
    def gather_data(self, params: dict) -> dict:
        """Phase 1: Gather data from database and RAG corpus."""
        ...

    @abstractmethod
    def analyze(self, gathered_data: dict, params: dict) -> dict:
        """Phase 2: Analyze with LLM."""
        ...

    @abstractmethod
    def generate_output(self, analysis: dict, params: dict) -> dict:
        """Phase 3: Generate output artifact."""
        ...

    def _summarize(self, result: Any) -> str:
        """Summarize a result for tracing without dumping full data."""
        if isinstance(result, dict):
            return f"dict with {len(result)} keys: {list(result.keys())}"
        return str(result)[:200]

    def _persist_result(self, task_id: str, result: dict) -> None:
        """Persist the result and traces in the database.

        In production: update AgentTask with status and result,
        insert AgentTrace for each entry in self.traces.
        """
        # Placeholder — implement with your ORM session
        pass
