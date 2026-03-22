# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
# Ejemplo didáctico: patrones/agentes/approval_gate.py

class ApprovalGate:
    """Gate de aprobación humana en el bucle ReAct."""

    async def check_approval(self, tool_name: str, params: dict,
                              reasoning: str, session_id: str) -> dict:
        tool_config = get_tool_config(tool_name)

        if not tool_config.approval_required:
            return {"approved": True, "mode": "autonomous"}

        # Construir mensaje de aprobación para el usuario
        approval_request = {
            "type": "approval_required",
            "tool": tool_name,
            "params_summary": summarize_params(params),
            "reasoning": reasoning,  # Por qué el agente quiere ejecutar esto
            "estimated_cost": estimate_tool_cost(tool_name, params),
            "session_id": session_id,
            "expires_at": datetime.utcnow() + timedelta(minutes=15),
        }

        # Persistir en Redis y notificar al frontend via SSE
        await store_pending_approval(session_id, approval_request)
        await notify_user_sse(session_id, approval_request)

        return {"approved": False, "mode": "waiting_approval",
                "approval_id": approval_request["id"]}
