# Extraído de: LibroCISO/cap-13-orquestador-copiloto.md
# Ejemplo didáctico: patrones/ai/copilot_audit.py

async def log_copilot_execution(
    db: AsyncSession,
    execution_id: str,
    request: CopilotRequest,
    mode: CopilotMode,
    steps: list[OrchestratorStep],
    total_tokens: int,
    total_cost_eur: float,
    duration_ms: int,
    status: str,  # completed | partial | failed
):
    """
    Registra la ejecución completa del copiloto en audit_trail.
    Esta función se llama SIEMPRE, incluso cuando la ejecución falla.
    """
    audit_entry = AuditTrail(
        action="copilot_execution",
        entity_type="copilot",
        entity_id=execution_id,
        user_id=request.user_id,
        corporate_id=request.tenant_id,
        details={
            "message_preview": request.message[:200],  # Truncar para no almacenar mensajes completos
            "module_context": request.module_context,
            "mode": mode.value,
            "status": status,
            "steps": [
                {
                    "agent": s.agent_name,
                    "action": s.action,
                    "status": s.status,
                    "tokens": s.tokens_used,
                    "cost_eur": round(s.cost_eur, 4),
                    "duration_ms": s.duration_ms,
                }
                for s in steps
            ],
            "totals": {
                "tokens": total_tokens,
                "cost_eur": round(total_cost_eur, 4),
                "duration_ms": duration_ms,
            },
        },
    )
    db.add(audit_entry)
    await db.commit()
