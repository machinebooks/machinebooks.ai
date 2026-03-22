# Extraído de: LibroCyberrange/cap-04-claude-ecosistema.md
# Tracking de uso de LLM para cada servicio
# Ejemplo didáctico: patrones/observabilidad/llm_tracker.py

from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class LLMUsageRecord:
    """Registro de uso de un modelo de lenguaje."""
    service_name: str        # Ej: "scenario_generator", "adaptive_coach"
    model: str               # Ej: "claude-sonnet-4-6"
    input_tokens: int
    output_tokens: int
    latency_ms: int
    user_id: int | None
    exercise_id: int | None
    success: bool
    timestamp: datetime

def track_llm_usage(
    service_name: str,
    model: str,
    response: "anthropic.types.Message",
    user_id: int = None,
    exercise_id: int = None
) -> LLMUsageRecord:
    """Registra el uso de un modelo tras cada llamada.

    Estos datos alimentan el dashboard de costes por servicio
    y permiten detectar anomalías (loops de agente, documentos
    excesivamente largos, ataques de prompt injection).
    """
    record = LLMUsageRecord(
        service_name=service_name,
        model=model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_ms=calculate_latency(),
        user_id=user_id,
        exercise_id=exercise_id,
        success=response.stop_reason != "error",
        timestamp=datetime.now(timezone.utc)
    )

    # Persistir en base de datos
    db.session.add(LLMUsageLog.from_record(record))
    db.session.commit()

    # Alerta si el consumo supera umbrales
    if record.output_tokens > 4000 and service_name == "adaptive_coach":
        alert_anomalous_usage(record)  # Un coach no debería generar 4K tokens

    return record
