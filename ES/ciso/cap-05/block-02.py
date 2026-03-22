# Extraído de: LibroCISO/cap-05-dpia-derechos.md
# Endpoint de resolución de solicitud de derechos ARCO+
# Concentra las validaciones regulatorias más relevantes

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user, require_permission
from app.models.privacy import SubjectRightsRequest, RequestStatus
from app.schemas.privacy import RightsRequestResolve, RightsRequestResponse

router = APIRouter(
    prefix="/api/v1/rights-requests", tags=["privacy-rights"]
)


@router.post("/{request_id}/resolve",
             response_model=RightsRequestResponse)
async def resolve_rights_request(
    request_id: int,
    data: RightsRequestResolve,
    current_user=Depends(get_current_user),
    _=Depends(require_permission("privacy:rights_resolve"))
):
    """Resuelve una solicitud de derechos.

    Valida que el plazo legal no se haya excedido.
    Si se deniega, exige motivación (Art. 12.4 RGPD).
    """
    request = await get_request_or_404(request_id, current_user)

    if request.status not in (
        RequestStatus.IN_PROGRESS, RequestStatus.EXTENDED
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede resolver una solicitud en estado "
                   f"'{request.status.value}'. Debe estar 'in_progress' "
                   f"o 'extended'."
        )

    # Verificar plazo legal
    now = datetime.utcnow()
    if now > request.deadline_date:
        # Permitir resolución tardía pero registrar incumplimiento
        await audit_log(
            action="rights_request.deadline_exceeded",
            resource_id=request.id,
            user_id=current_user.id,
            details={
                "deadline": request.deadline_date.isoformat(),
                "resolved_at": now.isoformat(),
                "days_overdue": (now - request.deadline_date).days,
            }
        )

    # Si se deniega, la motivación es obligatoria (Art. 12.4)
    if data.resolution == "denied" and not data.denial_reason:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La denegación requiere motivación obligatoria "
                   "(Art. 12.4 RGPD). Indique el motivo."
        )

    request.status = RequestStatus.RESOLVED
    request.resolution = data.resolution
    request.resolution_summary = data.resolution_summary
    request.denial_reason = data.denial_reason
    request.resolved_date = now
    request.updated_by = current_user.id

    await db.session.commit()

    await audit_log(
        action="rights_request.resolved",
        resource_id=request.id,
        user_id=current_user.id,
        details={
            "resolution": data.resolution,
            "within_deadline": now <= request.deadline_date,
        }
    )

    return request
