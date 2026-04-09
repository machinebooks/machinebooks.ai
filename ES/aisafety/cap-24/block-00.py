# Extraido de: LibroAISafety/cap-24-asl4-futuro.md
# Patrón de detección de comportamiento inconsistente
# entre evaluación y producción
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BehaviorProfile:
    """Perfil de comportamiento del modelo en un contexto dado."""
    context: str                # "evaluation" o "production"
    refusal_rate: float         # tasa de rechazo de peticiones peligrosas
    tool_call_diversity: float  # diversidad de herramientas invocadas
    response_length_avg: float  # longitud media de respuesta
    reasoning_depth: float      # profundidad de razonamiento (medida por tokens)
    timestamp: datetime

def detect_behavior_divergence(
    eval_profiles: list[BehaviorProfile],
    prod_profiles: list[BehaviorProfile],
    threshold: float = 0.15,  # 15% de divergencia es alertable
) -> list[str]:
    """
    Compara el comportamiento del modelo entre evaluación y producción.
    Si la divergencia supera el umbral, puede indicar alignment faking.
    """
    alerts = []
    eval_avg_refusal = sum(p.refusal_rate for p in eval_profiles) / len(eval_profiles)
    prod_avg_refusal = sum(p.refusal_rate for p in prod_profiles) / len(prod_profiles)

    # Si el modelo rechaza significativamente menos en producción
    # que en evaluación, es una señal de alarma
    if eval_avg_refusal - prod_avg_refusal > threshold:
        alerts.append(
            f"Divergencia en tasa de rechazo: eval={eval_avg_refusal:.2%}, "
            f"prod={prod_avg_refusal:.2%}. "
            f"Posible alignment faking — investigar."
        )

    eval_avg_depth = sum(p.reasoning_depth for p in eval_profiles) / len(eval_profiles)
    prod_avg_depth = sum(p.reasoning_depth for p in prod_profiles) / len(prod_profiles)

    # Si el modelo razona más profundamente en producción
    # (posible signo de planificación oculta)
    if prod_avg_depth - eval_avg_depth > threshold * 100:
        alerts.append(
            f"Divergencia en profundidad de razonamiento: eval={eval_avg_depth:.0f}, "
            f"prod={prod_avg_depth:.0f}. "
            f"Posible comportamiento de planificación no visto en evaluación."
        )

    return alerts
