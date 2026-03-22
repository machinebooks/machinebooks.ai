# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func


# Pesos de severidad para el cálculo de deuda
SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 10,
    Severity.HIGH: 5,
    Severity.MEDIUM: 2,
    Severity.LOW: 1
}

# Factor de antigüedad: la deuda crece con el tiempo
def age_factor(approved_at: datetime) -> float:
    """Penalización por antigüedad: crece un 10% cada 30 días."""
    days = (datetime.utcnow() - approved_at).days
    return 1.0 + (days / 30) * 0.1


def calculate_security_debt(db: Session) -> dict:
    """Calcula métricas de deuda de seguridad agregadas."""

    active = (
        db.query(SecurityException)
        .filter(SecurityException.status == ExceptionStatus.APPROVED)
        .all()
    )

    total_debt_score = 0
    debt_by_severity = {s: 0 for s in Severity}
    debt_by_service = {}

    for exc in active:
        weight = SEVERITY_WEIGHTS[exc.severity]
        age = age_factor(exc.approved_at)
        score = weight * age

        total_debt_score += score
        debt_by_severity[exc.severity] += score
        debt_by_service.setdefault(exc.service_name, 0)
        debt_by_service[exc.service_name] += score

    # Métricas adicionales
    avg_age_days = 0
    if active:
        ages = [(datetime.utcnow() - e.approved_at).days for e in active]
        avg_age_days = sum(ages) / len(ages)

    expired_unresolved = (
        db.query(func.count(SecurityException.id))
        .filter(SecurityException.status == ExceptionStatus.EXPIRED)
        .scalar()
    )

    return {
        "total_active_exceptions": len(active),
        "total_debt_score": round(total_debt_score, 1),
        "debt_by_severity": {
            s.value: round(v, 1) for s, v in debt_by_severity.items()
        },
        "debt_by_service": {
            k: round(v, 1) for k, v in sorted(
                debt_by_service.items(),
                key=lambda x: x[1],
                reverse=True
            )
        },
        "average_exception_age_days": round(avg_age_days, 1),
        "expired_unresolved": expired_unresolved,
        "health": (
            "critical" if any(
                e.severity == Severity.CRITICAL for e in active
            ) else "warning" if total_debt_score > 50
            else "healthy"
        )
    }
