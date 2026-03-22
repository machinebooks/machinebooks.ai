# Extraído de: LibroFinOps/cap-08-routing-modelos.md
# tasks/routing_audit.py
import random
from celery import shared_task
import anthropic
from models.llm_usage_log import LLMUsageLog

AUDIT_SAMPLE_SIZE = 50  # llamadas por semana

JUDGE_PROMPT = """Clasifica la siguiente tarea LLM en uno de estos niveles:
- FAST: clasificación, extracción, validación, respuesta binaria
- BALANCED: generación guiada, resumen, análisis con criterios definidos
- POWERFUL: razonamiento complejo, decisiones sin precedente, análisis abierto

Prompt analizado:
{prompt}

Responde solo con: FAST, BALANCED o POWERFUL."""

@shared_task
def audit_routing_sample():
    """
    Evalúa una muestra de llamadas para detectar routing subóptimo.
    Usa claude-haiku-4-5 como juez (bajo coste de auditoría).
    """
    client = anthropic.Anthropic()
    # Obtener muestra aleatoria de la última semana
    recent_logs = get_recent_llm_logs(days=7, limit=500)
    sample = random.sample(recent_logs, min(AUDIT_SAMPLE_SIZE, len(recent_logs)))

    mismatches = []
    for log in sample:
        response = client.messages.create(
            model="claude-haiku-4-5",  # juez económico
            max_tokens=10,
            messages=[{"role": "user", "content": JUDGE_PROMPT.format(
                prompt=log.prompt_preview  # primeros 500 chars
            )}],
        )
        judge_tier = response.content[0].text.strip()
        actual_tier = log.model_tier  # tier que se usó en producción

        if judge_tier != actual_tier:
            mismatches.append({
                "log_id": log.id,
                "service": log.service_name,
                "actual": actual_tier,
                "suggested": judge_tier,
            })

    # Publicar resultado en el dashboard de auditoría
    publish_routing_audit(mismatches, sample_size=len(sample))
    return len(mismatches)
