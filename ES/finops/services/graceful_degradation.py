# Extraído de: LibroFinOps/cap-11-presupuestos-circuit-breakers.md
# services/graceful_degradation.py
from enum import Enum
from middleware.budget_enforcement import BudgetAction, BudgetExceededException

class DegradationStrategy(str, Enum):
    """Estrategia de degradación por tipo de servicio."""
    INFORM_USER    = "inform_user"      # mostrar mensaje al usuario
    QUEUE_DEFERRED = "queue_deferred"   # encolar para procesamiento posterior
    STOP_SILENTLY  = "stop_silently"    # detener sin impacto visible

# Mapa de servicio a estrategia de degradación
SERVICE_DEGRADATION = {
    "chat_assistant":     DegradationStrategy.INFORM_USER,
    "proposal_section":   DegradationStrategy.QUEUE_DEFERRED,
    "index_updater":      DegradationStrategy.STOP_SILENTLY,
    "document_classifier": DegradationStrategy.QUEUE_DEFERRED,
    "risk_evaluator":     DegradationStrategy.INFORM_USER,
}

DEGRADATION_MESSAGES = {
    DegradationStrategy.INFORM_USER: (
        "El servicio de IA opera con capacidad reducida. "
        "Las respuestas pueden tardar más de lo habitual."
    ),
    DegradationStrategy.QUEUE_DEFERRED: (
        "La solicitud se ha encolado y se procesará cuando haya "
        "capacidad disponible (máximo 24 horas)."
    ),
}

def handle_budget_exceeded(
    service_name: str,
    exc: BudgetExceededException,
) -> dict:
    """
    Gestiona un presupuesto agotado con degradación gradual
    en lugar de un error genérico.
    """
    strategy = SERVICE_DEGRADATION.get(
        service_name, DegradationStrategy.QUEUE_DEFERRED
    )

    if strategy == DegradationStrategy.INFORM_USER:
        return {
            "status": "degraded",
            "message": DEGRADATION_MESSAGES[strategy],
            "retry_after_seconds": 300,
        }
    elif strategy == DegradationStrategy.QUEUE_DEFERRED:
        # Encolar la tarea para procesamiento diferido
        queue_for_later(service_name, exc.request_data)
        return {
            "status": "queued",
            "message": DEGRADATION_MESSAGES[strategy],
        }
    else:
        # STOP_SILENTLY: no hay mensaje, el servicio simplemente se detiene
        return {"status": "stopped"}
