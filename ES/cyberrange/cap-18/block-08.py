# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/coaching_metrics.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func

@dataclass
class CoachingMetrics:
    """Métricas agregadas del sistema de coaching."""

    # Volumen
    total_reactive_hints: int
    total_proactive_hints: int
    total_evaluations: int

    # Eficacia
    avg_stall_time_before_hint_min: float
    avg_stall_time_after_hint_min: float   # Tiempo hasta siguiente acción
    completion_rate_with_coaching: float    # % que completa usando coaching
    completion_rate_without_coaching: float

    # Calidad percibida
    avg_hint_rating: float                 # Media de ratings 1-5
    hint_rating_distribution: Dict[int, int]  # {1: N, 2: N, ...}

    # Coste
    total_tokens_used: int
    total_cost_usd: float
    avg_cost_per_session: float

def calculate_coaching_metrics(
    db: Session,
    period_start: datetime,
    period_end: datetime
) -> CoachingMetrics:
    """
    Calcula métricas de coaching para un período.
    Usado por el dashboard de administración.
    """
    # Consultas agregadas contra las tablas de coaching
    # ... (implementación con SQLAlchemy)

    return CoachingMetrics(
        total_reactive_hints=reactive_count,
        total_proactive_hints=proactive_count,
        total_evaluations=eval_count,
        avg_stall_time_before_hint_min=avg_before,
        avg_stall_time_after_hint_min=avg_after,
        completion_rate_with_coaching=rate_with,
        completion_rate_without_coaching=rate_without,
        avg_hint_rating=avg_rating,
        hint_rating_distribution=distribution,
        total_tokens_used=tokens,
        total_cost_usd=cost,
        avg_cost_per_session=cost_per_session,
    )
