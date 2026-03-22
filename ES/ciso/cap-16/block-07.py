# Extraído de: LibroCISO/cap-16-rbac-multitenancy.md
from fastapi import APIRouter, Depends, HTTPException, Request
from app.auth.permissions import require_permission
from app.auth.license import RequireModule
from app.repositories.base import BaseRepository, OptimisticLockError
from app.models.risk import RiskAssessment
from app.schemas.risk import RiskAssessmentCreate, RiskAssessmentUpdate
from app.database import get_db

router = APIRouter(prefix="/api/v1/risks", tags=["risk"])


@router.get(
    "/assessments",
    dependencies=[
        Depends(require_permission("risk", "read")),   # ← RBAC
        Depends(RequireModule("risk")),                  # ← Licencia
    ]
)
async def list_risk_assessments(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db=Depends(get_db)
):
    """Listar evaluaciones de riesgo del tenant actual.

    Protecciones aplicadas automáticamente:
    1. JWT verificado por AuthMiddleware (cap. 15)
    2. corporate_id inyectado por TenantMiddleware
    3. Permiso risk:read verificado por require_permission
    4. Módulo 'risk' licenciado verificado por RequireModule
    5. Query filtrada por corporate_id en BaseRepository
    """
    repo = BaseRepository(
        model=RiskAssessment,
        session=db,
        corporate_id=request.state.corporate_id  # ← Del middleware
    )
    assessments = await repo.get_all(skip=skip, limit=limit)
    return {"items": assessments, "total": len(assessments)}


@router.put(
    "/assessments/{assessment_id}",
    dependencies=[
        Depends(require_permission("risk", "write")),
        Depends(RequireModule("risk")),
    ]
)
async def update_risk_assessment(
    assessment_id: int,
    payload: RiskAssessmentUpdate,
    request: Request,
    db=Depends(get_db)
):
    """Actualizar evaluación de riesgo con versionado optimista.

    El payload DEBE incluir 'version' — el número de versión
    que el cliente leyó al obtener la entidad.
    """
    repo = BaseRepository(
        model=RiskAssessment,
        session=db,
        corporate_id=request.state.corporate_id
    )
    entity = await repo.get_by_id(assessment_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    try:
        # Aplicar cambios con verificación de versión
        for field, value in payload.dict(exclude_unset=True, exclude={"version"}).items():
            setattr(entity, field, value)

        updated = await repo.update(
            entity=entity,
            user_id=request.state.user_id,
            expected_version=payload.version  # ← Versionado optimista
        )
        await db.commit()
        return updated

    except OptimisticLockError as e:
        raise HTTPException(status_code=409, detail=str(e))
