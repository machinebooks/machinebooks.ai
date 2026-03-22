# Extraído de: LibroCISO/cap-09-nis2-dora-tsunami.md
# Router NIS2 — todos los endpoints requieren licencia NIS2 activa
# El middleware RequireModule se aplica a nivel de router completo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.modules.licensing import RequireModule, ModuleName
from app.models.nis2 import NIS2Incident, NIS2Notification, NIS2NotificationPhase


router = APIRouter(
    prefix="/api/v1/nis2",
    tags=["NIS2"],
    dependencies=[Depends(RequireModule(ModuleName.NIS2))]
    # ↑ Todas las rutas de este router requieren licencia NIS2
)


@router.post("/incidents", status_code=status.HTTP_201_CREATED)
def create_nis2_incident(
    data: NIS2IncidentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registra un incidente NIS2 y crea automáticamente
    las tres notificaciones con sus plazos.
    """
    # Calcular plazos desde el momento de conocimiento (Art. 23 NIS2)
    awareness = data.awareness_at

    incident = NIS2Incident(
        corporate_id=current_user.corporate_id,
        created_by=current_user.id,
        incident_code=generate_incident_code(db, current_user.corporate_id),
        awareness_at=awareness,
        # Plazos Art. 23 NIS2 — calculados automáticamente
        early_warning_deadline=awareness + timedelta(hours=24),
        formal_notification_deadline=awareness + timedelta(hours=72),
        final_report_deadline=awareness + timedelta(days=30),
        # El resto de campos (title, description, severity, etc.)
        # se copian directamente del schema de entrada
        **data.dict(exclude={"awareness_at"})
    )
    db.add(incident)
    db.flush()

    # Crear las tres notificaciones automáticamente
    phases = [
        (NIS2NotificationPhase.EARLY_WARNING,
         awareness + timedelta(hours=24)),
        (NIS2NotificationPhase.FORMAL_NOTIFICATION,
         awareness + timedelta(hours=72)),
        (NIS2NotificationPhase.FINAL_REPORT,
         awareness + timedelta(days=30)),
    ]

    for phase, deadline in phases:
        notification = NIS2Notification(
            corporate_id=current_user.corporate_id,
            created_by=current_user.id,
            incident_id=incident.id,
            phase=phase,
            deadline=deadline,
            status="pending"
        )
        db.add(notification)

    db.commit()
    # + audit trail y respuesta con plazos calculados (omitido por brevedad)
