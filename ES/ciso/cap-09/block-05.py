# Extraído de: LibroCISO/cap-09-nis2-dora-tsunami.md
# Tarea programada: verificación diaria de licencias
# Se ejecuta cada noche a las 02:00 vía Celery Beat

from datetime import datetime, timezone, timedelta
from celery import shared_task
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.license import LicenseModule, LicenseStatus
from app.services.notifications import send_internal_alert


@shared_task(name="license.check_expirations")
def check_license_expirations():
    """Verifica expiración de licencias y genera alertas.

    Tres acciones:
    1. Licencias expiradas → cambiar estado a EXPIRED
    2. Licencias que expiran en <30 días → alerta al admin
    3. Licencias que expiran en <7 días → alerta urgente
    """
    db: Session = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        # 1. Marcar licencias expiradas
        expired = db.query(LicenseModule).filter(
            LicenseModule.status == LicenseStatus.ACTIVE,
            LicenseModule.expires_at < now,
            LicenseModule.is_deleted == False
        ).all()

        for lic in expired:
            lic.status = LicenseStatus.EXPIRED
            send_internal_alert(
                corporate_id=lic.corporate_id,
                level="warning",
                title=f"Licencia expirada: {lic.display_name}",
                message=f"La licencia del módulo {lic.display_name} "
                        f"expiró el {lic.expires_at.strftime('%d/%m/%Y')}. "
                        f"Los endpoints del módulo ya no son accesibles."
            )

        # 2. Alertas de expiración próxima (30 días)
        threshold_30 = now + timedelta(days=30)
        expiring_soon = db.query(LicenseModule).filter(
            LicenseModule.status == LicenseStatus.ACTIVE,
            LicenseModule.expires_at.between(now, threshold_30),
            LicenseModule.is_deleted == False
        ).all()

        for lic in expiring_soon:
            days_left = (lic.expires_at - now).days
            level = "critical" if days_left <= 7 else "warning"
            send_internal_alert(
                corporate_id=lic.corporate_id,
                level=level,
                title=f"Licencia próxima a expirar: {lic.display_name}",
                message=f"La licencia del módulo {lic.display_name} "
                        f"expira en {days_left} días "
                        f"({lic.expires_at.strftime('%d/%m/%Y')})."
            )

        db.commit()

        return {
            "expired_count": len(expired),
            "expiring_soon_count": len(expiring_soon),
            "checked_at": now.isoformat()
        }

    finally:
        db.close()
