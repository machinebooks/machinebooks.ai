# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
def request_human_approval(
    self,
    execution_id: str,
    step: WorkflowStep,
    proposed_action: dict
) -> dict:
    """
    Pausa el workflow y solicita aprobación humana para el siguiente paso.
    El estado persiste con los detalles de la acción propuesta.
    """
    state_key = f"workflow_state:{execution_id}"
    state = json.loads(self.redis.get(state_key))

    # Construir el mensaje de aprobación con contexto suficiente
    approval_request = {
        "execution_id": execution_id,
        "workflow_name": self.workflows[state["workflow_id"]].name,
        "step_name": step.name,
        "step_description": step.description,
        "proposed_action": proposed_action,
        "previous_results_summary": self._summarize_results(state["step_results"]),
        "requested_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=8)).isoformat()
    }

    state["status"] = "awaiting_approval"
    state["pending_approval"] = approval_request
    self.redis.setex(state_key, self.STATE_TTL, json.dumps(state))

    return approval_request

def resume_after_approval(self, execution_id: str, approved: bool) -> dict:
    """
    Reanuda el workflow tras la decisión humana.
    Si se rechaza, el workflow termina con estado 'rejected'.
    """
    state_key = f"workflow_state:{execution_id}"
    state = json.loads(self.redis.get(state_key))

    if not approved:
        state["status"] = "rejected"
        self.redis.setex(state_key, self.STATE_TTL, json.dumps(state))
        return {"status": "rejected", "message": "Workflow cancelado por el usuario."}

    # Limpiar el estado de espera y continuar
    pending = state.pop("pending_approval")
    state["status"] = "running"
    self.redis.setex(state_key, self.STATE_TTL, json.dumps(state))

    # Ejecutar el paso aprobado
    return self.advance_step(execution_id, pending["proposed_action"])
