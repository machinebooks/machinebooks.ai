# Extraído de: LibroCISO/cap-12-agentes-especializados.md
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional
import time


class BaseAgent(ABC):
    """Clase base para todos los agentes del GRC.

    Impone un lifecycle de tres fases (gather, analyze, generate)
    y registra tracing automático por fase.
    """

    def __init__(self, agent_name: str, llm_service, db_session):
        self.agent_name = agent_name
        self.llm_service = llm_service
        self.db_session = db_session
        self.traces: list[dict] = []
        self.total_tokens = 0
        self.total_cost = 0.0

    def execute(self, task_id: str, params: dict) -> dict:
        """Ejecuta el lifecycle completo con tracing automático.

        Este método NO se sobreescribe. Los agentes hijos
        implementan gather_data, analyze y generate_output.
        """
        result = {"task_id": task_id, "agent": self.agent_name}

        try:
            # Fase 1: Recopilar datos
            gathered = self._traced_phase(
                "gather_data", task_id,
                lambda: self.gather_data(params)
            )

            # Fase 2: Analizar con LLM
            analysis = self._traced_phase(
                "analyze", task_id,
                lambda: self.analyze(gathered, params)
            )

            # Fase 3: Generar artefacto de salida
            output = self._traced_phase(
                "generate_output", task_id,
                lambda: self.generate_output(analysis, params)
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
                "message": str(e)
            })

        # Persistir resultado y trazas en BD
        self._persist_result(task_id, result)
        return result

    def _traced_phase(self, phase_name: str, task_id: str,
                      fn: callable) -> Any:
        """Envuelve una fase en tracing automático."""
        start = time.monotonic()
        tokens_before = self.total_tokens

        result = fn()

        duration_ms = int((time.monotonic() - start) * 1000)
        tokens_used = self.total_tokens - tokens_before

        self._record_trace(task_id, phase_name, {
            "duration_ms": duration_ms,
            "tokens_used": tokens_used,
            "result_summary": self._summarize(result)
        })

        return result

    def _record_trace(self, task_id: str, phase: str,
                      data: dict) -> None:
        """Registra una entrada de tracing."""
        trace = {
            "task_id": task_id,
            "agent": self.agent_name,
            "phase": phase,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        self.traces.append(trace)

    @abstractmethod
    def gather_data(self, params: dict) -> dict:
        """Fase 1: Recopilar datos de BD y RAG."""
        ...

    @abstractmethod
    def analyze(self, gathered_data: dict, params: dict) -> dict:
        """Fase 2: Analizar con LLM."""
        ...

    @abstractmethod
    def generate_output(self, analysis: dict,
                        params: dict) -> dict:
        """Fase 3: Generar artefacto de salida."""
        ...

    def _summarize(self, result: Any) -> str:
        """Resume un resultado para el tracing sin volcar datos completos."""
        if isinstance(result, dict):
            return f"dict con {len(result)} claves: {list(result.keys())}"
        return str(result)[:200]

    def _persist_result(self, task_id: str, result: dict) -> None:
        """Persiste el resultado y las trazas en la BD."""
        # Actualizar AgentTask con estado y resultado
        # Insertar AgentTrace por cada entrada de self.traces
        ...
