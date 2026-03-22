# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
from datetime import datetime, timedelta
from sqlalchemy.orm import Session


def review_active_exceptions(db: Session) -> list[dict]:
    """Revisa excepciones activas y genera acciones."""

    actions = []
    now = datetime.utcnow()

    # Excepciones expiradas que no se han resuelto
    expired = (
        db.query(SecurityException)
        .filter(
            SecurityException.status == ExceptionStatus.APPROVED,
            SecurityException.expires_at <= now
        )
        .all()
    )

    for exc in expired:
        exc.status = ExceptionStatus.EXPIRED
        actions.append({
            "action": "expired",
            "exception_id": exc.id,
            "finding_id": exc.finding_id,
            "owner": exc.requested_by,
            "message": (
                f"Excepción {exc.id} para {exc.finding_id} ha expirado. "
                f"El hallazgo volverá a bloquear el pipeline."
            )
        })

    # Excepciones que expiran en los próximos 14 días
    expiring_soon = (
        db.query(SecurityException)
        .filter(
            SecurityException.status == ExceptionStatus.APPROVED,
            SecurityException.expires_at > now,
            SecurityException.expires_at <= now + timedelta(days=14)
        )
        .all()
    )

    for exc in expiring_soon:
        days_left = (exc.expires_at - now).days
        actions.append({
            "action": "expiring_soon",
            "exception_id": exc.id,
            "finding_id": exc.finding_id,
            "owner": exc.requested_by,
            "days_remaining": days_left,
            "can_renew": exc.renewal_count < exc.max_renewals,
            "message": (
                f"Excepción {exc.id} expira en {days_left} días. "
                f"{'Puede renovarse.' if exc.renewal_count < exc.max_renewals else 'No quedan renovaciones. Debe resolverse.'}"
            )
        })

    db.commit()
    return actions
