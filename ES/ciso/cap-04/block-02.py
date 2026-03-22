# Extraído de: LibroCISO/cap-04-registro-tratamientos.md
# Endpoint REST para gestión de tratamientos
# FastAPI con validación Pydantic por estado

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user, require_permission
from app.models.privacy import DataProcessingActivity
from app.schemas.privacy import (
    ProcessingActivityCreate,
    ProcessingActivityActivate,
    ProcessingActivityResponse
)

router = APIRouter(prefix="/api/v1/processing-activities", tags=["privacy"])


@router.post("/", response_model=ProcessingActivityResponse,
             status_code=status.HTTP_201_CREATED)
async def create_processing_activity(
    data: ProcessingActivityCreate,
    current_user=Depends(get_current_user),
    _=Depends(require_permission("privacy:write"))
):
    """Crea un tratamiento en estado borrador.

    Requiere permiso 'privacy:write'.
    El corporate_id se inyecta desde el token del usuario.
    """
    activity = DataProcessingActivity(
        **data.model_dump(),
        corporate_id=current_user.corporate_id,
        created_by=current_user.id,
        status="draft"
    )
    db.session.add(activity)
    await db.session.commit()
    return activity


@router.post("/{activity_id}/activate",
             response_model=ProcessingActivityResponse)
async def activate_processing_activity(
    activity_id: int,
    data: ProcessingActivityActivate,
    current_user=Depends(get_current_user),
    _=Depends(require_permission("privacy:activate"))
):
    """Activa un tratamiento — validación completa Art. 30.

    Solo el DPO o un rol con 'privacy:activate' puede activar.
    Pydantic valida que todos los campos obligatorios del Art. 30
    estén presentes antes de persistir el cambio.
    """
    activity = await get_activity_or_404(activity_id, current_user)

    if activity.status == "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El tratamiento ya está activo"
        )

    # La validación la hace ProcessingActivityActivate
    # Si falta un campo obligatorio, Pydantic lanza 422
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)

    activity.status = "active"
    activity.updated_by = current_user.id

    # Si hay categorías especiales, marcar como alto riesgo
    if activity.special_categories:
        activity.risk_level = "high"
        activity.dpia_required = True

    await db.session.commit()

    # Auditoría: registrar activación en audit_trail
    await audit_log(
        action="processing_activity.activated",
        resource_id=activity.id,
        user_id=current_user.id,
        details={"legal_basis": activity.legal_basis.value}
    )

    return activity
