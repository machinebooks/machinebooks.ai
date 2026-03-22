# Extraído de: LibroFinOps/cap-08-routing-modelos.md
# tasks/routing_quality_sampling.py
import random
from celery import shared_task
import anthropic
from models.llm_usage_log import LLMUsageLog
import logging

logger = logging.getLogger(__name__)

QUALITY_JUDGE_PROMPT = """Eres un evaluador de calidad de respuestas de IA.

Se te proporcionan:
1. Un PROMPT original enviado a un modelo LLM.
2. La RESPUESTA que produjo un modelo de menor capacidad.

Evalúa si la RESPUESTA es adecuada para el PROMPT.

Criterios:
- ¿La respuesta es correcta factualmente?
- ¿Cubre todos los aspectos solicitados?
- ¿El nivel de detalle es suficiente para la tarea?
- ¿El formato es el esperado?

Responde con un JSON:
{{
  "quality": "acceptable" | "improvable" | "unacceptable",
  "reason": "explicación breve",
  "would_opus_differ": true | false
}}"""

SAMPLE_RATE = 0.05  # 5 % de las llamadas

@shared_task
def sample_and_evaluate():
    """
    Recoge llamadas marcadas para auditoría de calidad
    y las re-evalúa con opus como juez.
    Coste estimado: $0,15-0,40 por ejecución diaria.
    """
    client = anthropic.Anthropic()
    from database import get_db
    db = next(get_db())

    # Obtener llamadas marcadas para auditoría en las últimas 24h
    marked_logs = db.query(LLMUsageLog).filter(
        LLMUsageLog.quality_audit_pending == True,
        LLMUsageLog.model_tier.in_(["fast", "balanced"]),
    ).limit(30).all()  # máximo 30 evaluaciones por día

    results = {"acceptable": 0, "improvable": 0, "unacceptable": 0}
    problematic_services = []

    for log in marked_logs:
        try:
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{"role": "user", "content": (
                    QUALITY_JUDGE_PROMPT
                    + f"\n\nPROMPT:\n{log.prompt_preview}\n\n"
                    + f"RESPUESTA:\n{log.response_preview}"
                )}],
            )

            import json
            judgment = json.loads(response.content[0].text)
            quality = judgment.get("quality", "improvable")
            results[quality] = results.get(quality, 0) + 1

            # Registrar resultado de auditoría
            log.quality_audit_result = quality
            log.quality_audit_pending = False

            if quality == "unacceptable":
                problematic_services.append({
                    "service": log.service_name,
                    "tier_used": log.model_tier,
                    "reason": judgment.get("reason", "sin detalle"),
                    "log_id": log.id,
                })

        except Exception as exc:
            logger.warning("Error evaluando log %d: %s", log.id, exc)
            log.quality_audit_pending = False

    db.commit()

    # Si más del 20 % de las muestras son inaceptables, alertar
    total = sum(results.values())
    if total > 0 and results["unacceptable"] / total > 0.20:
        publish_quality_alert(
            message=(
                f"Alerta de calidad de routing: {results['unacceptable']} de "
                f"{total} muestras evaluadas como inaceptables."
            ),
            details=problematic_services,
        )

    return {
        "evaluated": total,
        "results": results,
        "problematic_services": len(problematic_services),
    }


def mark_for_quality_audit(log_id: int, db):
    """
    Marca una llamada para auditoría de calidad.
    Se invoca desde LLMService.complete() con probabilidad SAMPLE_RATE.
    """
    if random.random() < SAMPLE_RATE:
        db.query(LLMUsageLog).filter(
            LLMUsageLog.id == log_id
        ).update({"quality_audit_pending": True})
