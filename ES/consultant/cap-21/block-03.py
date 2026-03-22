# Extraído de: LibroConsultor/cap-21-productizacion.md
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Optional

class PlanType(Enum):
    SINGLE = "single"           # Un assessment, sin recurrencia
    QUARTERLY = "quarterly"     # Assessment cada 3 meses + consultor
    CONTINUOUS = "continuous"   # Assessment trimestral + monitorización

@dataclass
class Subscription:
    client_id: str
    plan: PlanType
    start_date: date
    price_eur: float
    consultant_hours_included: float  # Horas de consultor por periodo
    assessments_remaining: int
    next_assessment_date: Optional[date] = None

    @classmethod
    def create_quarterly(cls, client_id: str) -> "Subscription":
        """Plan trimestral: 4 assessments/año + 6h consultor."""
        return cls(
            client_id=client_id,
            plan=PlanType.QUARTERLY,
            start_date=date.today(),
            price_eur=4500.0,       # €4.500/año
            consultant_hours_included=6.0,  # Por trimestre
            assessments_remaining=4,
            next_assessment_date=date.today() + timedelta(days=90),
        )

    @classmethod
    def create_continuous(cls, client_id: str) -> "Subscription":
        """Plan continuo: assessments + monitorización + 12h consultor."""
        return cls(
            client_id=client_id,
            plan=PlanType.CONTINUOUS,
            start_date=date.today(),
            price_eur=9600.0,       # €9.600/año (€800/mes)
            consultant_hours_included=12.0,  # Por trimestre
            assessments_remaining=4,
            next_assessment_date=date.today() + timedelta(days=90),
        )

    def is_assessment_due(self) -> bool:
        """Comprueba si toca ejecutar un nuevo assessment."""
        if self.next_assessment_date is None:
            return False
        return date.today() >= self.next_assessment_date

    def record_assessment(self):
        """Registra un assessment completado y programa el siguiente."""
        self.assessments_remaining -= 1
        if self.assessments_remaining > 0:
            self.next_assessment_date = date.today() + timedelta(days=90)
        else:
            self.next_assessment_date = None

# Motor de alertas para suscripciones activas
def check_pending_assessments(
    subscriptions: list[Subscription]
) -> list[dict]:
    """Genera alertas para assessments que deben ejecutarse."""
    alerts = []
    for sub in subscriptions:
        if sub.is_assessment_due():
            alerts.append({
                "client_id": sub.client_id,
                "plan": sub.plan.value,
                "action": "assessment_due",
                "message": (
                    f"Assessment trimestral pendiente. "
                    f"Quedan {sub.assessments_remaining} en el periodo."
                ),
            })
    return alerts
