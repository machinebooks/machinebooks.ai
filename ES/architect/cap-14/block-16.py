# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
import redis
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkflowStep:
    step_id: str
    name: str
    tool_name: str                   # Herramienta a ejecutar en este paso
    input_mappings: dict             # Cómo obtener inputs desde contexto o pasos previos
    timeout_seconds: int = 60
    is_blocking: bool = True         # Si True, espera confirmación humana

@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    steps: list[WorkflowStep]
    total_timeout: int               # Timeout global del workflow completo
    trigger_patterns: list[str]      # Regex para auto-detectar activación

class WorkflowEngine:
    """
    Motor de ejecución de workflows con persistencia de estado en Redis.
    El estado se guarda con TTL de 24h para permitir reanudación.
    """

    STATE_TTL = 86400  # 24 horas en segundos

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.workflows = self._load_workflow_definitions()

    def detect_workflow(self, user_message: str) -> Optional[str]:
        """Detecta si el mensaje activa algún workflow predefinido."""
        for wf_id, wf_def in self.workflows.items():
            for pattern in wf_def.trigger_patterns:
                if re.search(pattern, user_message, re.IGNORECASE):
                    return wf_id
        return None

    def start_workflow(
        self,
        workflow_id: str,
        session_id: str,
        initial_context: dict
    ) -> str:
        """Inicia un workflow y persiste el estado inicial en Redis."""
        execution_id = f"wf:{workflow_id}:{session_id}:{uuid4().hex[:8]}"
        state = {
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "current_step": 0,
            "context": initial_context,
            "step_results": {},
            "status": "running",
            "started_at": datetime.utcnow().isoformat()
        }
        self.redis.setex(
            f"workflow_state:{execution_id}",
            self.STATE_TTL,
            json.dumps(state)
        )
        return execution_id

    def advance_step(self, execution_id: str, step_result: dict) -> dict:
        """
        Avanza el workflow al siguiente paso guardando el resultado del actual.
        Retorna el estado actualizado con instrucciones para el siguiente paso.
        """
        state_key = f"workflow_state:{execution_id}"
        state = json.loads(self.redis.get(state_key))

        wf_def = self.workflows[state["workflow_id"]]
        current_step = wf_def.steps[state["current_step"]]

        # Guardar resultado del paso actual
        state["step_results"][current_step.step_id] = step_result
        state["current_step"] += 1

        # Verificar si el workflow ha terminado
        if state["current_step"] >= len(wf_def.steps):
            state["status"] = "completed"
            self.redis.setex(state_key, self.STATE_TTL, json.dumps(state))
            return {"status": "completed", "final_results": state["step_results"]}

        # Preparar inputs para el siguiente paso
        next_step = wf_def.steps[state["current_step"]]
        next_inputs = self._resolve_input_mappings(next_step.input_mappings, state)

        self.redis.setex(state_key, self.STATE_TTL, json.dumps(state))
        return {
            "status": "next_step",
            "step_name": next_step.name,
            "tool_to_execute": next_step.tool_name,
            "inputs": next_inputs,
            "requires_human_approval": next_step.is_blocking
        }
