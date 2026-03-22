# Extraído de: LibroCISO/cap-22-observabilidad-siem.md
import structlog
from datetime import datetime, timezone

log = structlog.get_logger()


class AIAuditLogger:
    """Registra operaciones de IA para conformidad con AI Act Art. 12."""

    def log_ai_operation(
        self,
        operation_type: str,      # "risk_analysis", "dpia_generation", etc.
        agent_name: str,          # "RiskAgent", "PrivacyAgent", etc.
        model_used: str,          # "claude-sonnet-4-6"
        provider: str,            # "anthropic", "azure_openai"
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        estimated_cost_eur: float,
        guardrails_applied: list, # ["pii_filter", "topic_block"]
        guardrails_triggered: list,  # Guardrails que bloquearon contenido
        human_decision: str,      # "accepted", "rejected", "pending"
        user_id: str,
        corporate_id: str,
        request_id: str,
        input_summary: str,       # Resumen (no el prompt completo por PII)
        output_summary: str,      # Resumen de la respuesta
    ):
        """Registra una operación de IA completa para auditoría."""
        log.info(
            "ai_operation_completed",
            operation_type=operation_type,
            agent_name=agent_name,
            model_used=model_used,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            latency_ms=latency_ms,
            estimated_cost_eur=round(estimated_cost_eur, 6),
            guardrails_applied=guardrails_applied,
            guardrails_triggered=guardrails_triggered,
            human_decision=human_decision,
            user_id=user_id,
            corporate_id=corporate_id,
            request_id=request_id,
            # No loguear prompts completos: pueden contener PII
            input_summary=input_summary[:200],
            output_summary=output_summary[:200],
        )

        # Si un guardrail se disparó, evento de mayor severidad para SIEM
        if guardrails_triggered:
            from app.observability.cef_formatter import CEFFormatter
            cef = CEFFormatter()
            cef.send_to_siem("ai_guardrail_block", {
                "user_id": user_id,
                "corporate_id": corporate_id,
                "request_id": request_id,
                "path": f"/ai/{operation_type}",
                "method": "POST",
            })
