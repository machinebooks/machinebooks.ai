# Extraído de: LibroCISO/cap-06-brechas-encargados-transferencias.md
# Endpoint REST para registro de brechas
# FastAPI con cálculo automático de deadline Art. 33

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional

from app.core.auth import get_current_user, require_permission
from app.models.privacy import (
    DataBreach, BreachStatus, BreachSeverity, BreachType
)
from app.services.notifications import send_notification
from app.services.audit import audit_log


router = APIRouter(
    prefix="/api/v1/breaches",
    tags=["privacy-breaches"]
)


class BreachCreate(BaseModel):
    """Schema para registrar una nueva brecha."""
    title: str = Field(..., min_length=10, max_length=500)
    description: str = Field(..., min_length=20)
    breach_type: BreachType
    severity: BreachSeverity
    detected_at: Optional[datetime] = None  # Si None, usa now()
    affected_count: Optional[int] = None
    data_categories_affected: Optional[list[str]] = None
    special_categories_affected: bool = False
    root_cause: Optional[str] = None
    measures_taken: Optional[list[str]] = None


class BreachResponse(BaseModel):
    id: int
    code: str
    title: str
    status: str
    severity: str
    detected_at: datetime
    notification_deadline: datetime
    hours_remaining: float
    is_overdue: bool


@router.post("/", response_model=BreachResponse,
             status_code=status.HTTP_201_CREATED)
async def register_breach(
    data: BreachCreate,
    current_user=Depends(get_current_user),
    _=Depends(require_permission("privacy:breach:write"))
):
    """Registra una nueva brecha de datos personales.

    Calcula automáticamente:
    - notification_deadline = detected_at + 72 horas
    - Código secuencial: BREACH-YYYY-NNN

    Genera notificación inmediata al DPO y al CISO.
    """
    detected = data.detected_at or datetime.utcnow()
    deadline = detected + timedelta(hours=72)

    # Generar código secuencial
    year = detected.year
    count = await db.query(DataBreach).filter(
        DataBreach.code.like(f"BREACH-{year}-%")
    ).count()
    code = f"BREACH-{year}-{count + 1:03d}"

    breach = DataBreach(
        code=code,
        title=data.title,
        description=data.description,
        breach_type=data.breach_type,
        severity=data.severity,
        status=BreachStatus.DETECTED,
        detected_at=detected,
        notification_deadline=deadline,
        affected_count=data.affected_count,
        data_categories_affected=data.data_categories_affected,
        special_categories_affected=data.special_categories_affected,
        root_cause=data.root_cause,
        measures_taken=data.measures_taken,
        reported_by=current_user.id,
        corporate_id=current_user.corporate_id,
        created_by=current_user.id
    )

    db.session.add(breach)
    await db.session.commit()

    # Auditoría: registrar creación de brecha
    await audit_log(
        action="data_breach.registered",
        resource_id=breach.id,
        user_id=current_user.id,
        details={
            "code": code,
            "severity": data.severity.value,
            "deadline": deadline.isoformat(),
            "affected_count": data.affected_count
        }
    )

    # Notificación inmediata al DPO y CISO
    hours_left = (deadline - datetime.utcnow()).total_seconds() / 3600
    send_notification(
        recipients=["dpo", "ciso"],
        level="high" if data.severity in [
            BreachSeverity.HIGH, BreachSeverity.CRITICAL
        ] else "medium",
        title=f"Nueva brecha registrada: {code}",
        message=(
            f"Brecha: {data.title}\n"
            f"Severidad: {data.severity.value}\n"
            f"Tipo: {data.breach_type.value}\n"
            f"Deadline AEPD: {deadline.strftime('%d/%m/%Y %H:%M')} "
            f"({hours_left:.0f}h restantes)\n"
            f"Afectados estimados: {data.affected_count or 'Por determinar'}"
        ),
        breach_id=breach.id
    )

    return breach
