# Extraído de: LibroDevSecOps/cap-18-runtime-security.md
# runtime_analyzer/falco_agent.py
"""
Agente Claude que analiza alertas de Falco en runtime.
Recibe alertas vía HTTP webhook, las correlaciona con el
inventario de contenedores y emite un veredicto priorizado.
"""
import anthropic
from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI()
client = anthropic.Anthropic()

# Inventario de contenedores y su comportamiento esperado
CONTAINER_PROFILES = {
    "inference-service": {
        "expected_processes": ["python3", "gunicorn", "uvicorn"],
        "allowed_outbound": ["api.anthropic.com:443", "qdrant:6333"],
        "allowed_fs_write": ["/tmp", "/var/log"],
        "description": "Servicio de inferencia con Claude API"
    },
    "agent-worker": {
        "expected_processes": ["python3", "celery"],
        "allowed_outbound": ["api.anthropic.com:443", "redis:6379"],
        "allowed_fs_write": ["/tmp"],
        "description": "Worker de agentes Claude con tools limitadas"
    },
    "api-gateway": {
        "expected_processes": ["node", "nginx"],
        "allowed_outbound": ["inference-service:8000"],
        "allowed_fs_write": ["/var/log/nginx"],
        "description": "API gateway, sin acceso directo a LLM"
    }
}


class FalcoAlert(BaseModel):
    """Estructura de una alerta de Falco."""
    output: str
    priority: str
    rule: str
    time: str
    output_fields: dict
    tags: list[str] = []


def build_analysis_prompt(alert: FalcoAlert) -> str:
    """Construye el prompt de análisis con contexto del entorno."""
    container = alert.output_fields.get("container.name", "unknown")
    profile = CONTAINER_PROFILES.get(container, {})

    return f"""Analiza esta alerta de seguridad de Falco y clasifícala.

## Alerta
- Regla: {alert.rule}
- Prioridad: {alert.priority}
- Hora: {alert.time}
- Salida: {alert.output}
- Tags: {', '.join(alert.tags)}

## Contexto del contenedor
- Nombre: {container}
- Perfil esperado: {profile.get('description', 'No documentado')}
- Procesos permitidos: {profile.get('expected_processes', 'No definidos')}
- Conexiones salientes permitidas: {profile.get('allowed_outbound', 'No definidas')}
- Escrituras permitidas: {profile.get('allowed_fs_write', 'No definidas')}

## Instrucciones
1. Clasifica: TRUE_POSITIVE, FALSE_POSITIVE o NEEDS_INVESTIGATION
2. Explica en 2-3 frases por qué
3. Si es TRUE_POSITIVE, indica la severidad real (CRITICAL/HIGH/MEDIUM/LOW)
4. Si es TRUE_POSITIVE, sugiere la acción inmediata
5. Si es FALSE_POSITIVE, sugiere el ajuste de regla para evitar futuras alertas

Responde SOLO en formato JSON con las claves:
classification, explanation, real_severity, suggested_action, rule_adjustment"""


@app.post("/webhook/falco")
async def receive_falco_alert(request: Request):
    """Recibe alertas de Falco y las analiza con Claude."""
    payload = await request.json()
    alert = FalcoAlert(**payload)

    # Solo analizar alertas WARNING o superiores
    if alert.priority not in ("Warning", "Error", "Critical"):
        return {"status": "skipped", "reason": "low_priority"}

    prompt = build_analysis_prompt(alert)

    # Usar claude-haiku-4-5 para análisis rápido y económico
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = message.content[0].text

    # Registrar para auditoría y métricas
    log_analysis(alert, analysis)

    # Si es CRITICAL y TRUE_POSITIVE, escalar inmediatamente
    if (alert.priority == "Critical"
            and '"TRUE_POSITIVE"' in analysis):
        await escalate_to_oncall(alert, analysis)

    return {"status": "analyzed", "analysis": analysis}
