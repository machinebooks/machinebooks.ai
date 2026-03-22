# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
# Endpoint de matriz de riesgo — FastAPI
# Filtrado por methodology, con soporte para MAGERIT y FAIR

from fastapi import APIRouter, Depends, Query
from app.auth.dependencies import get_current_user
from app.services.risk_service import RiskService

router = APIRouter(prefix="/api/v1/risk", tags=["Risk Management"])


@router.get("/analyses/{analysis_id}/matrix")
async def get_risk_matrix(
    analysis_id: int,
    methodology: str = Query(
        ..., description="Metodología: magerit_v3, iso_27005, fair..."
    ),
    asset_type: str | None = Query(
        None, description="Filtrar por tipo de activo"
    ),
    risk_level: str | None = Query(
        None, description="Filtrar por nivel de riesgo"
    ),
    current_user=Depends(get_current_user),
    risk_service: RiskService = Depends(),
):
    """Devuelve la matriz de riesgo para un análisis.

    Para metodologías cualitativas: matriz 5×5 con conteo por celda.
    Para FAIR: distribución de ALE por rangos.

    Incluye:
    - Matriz (o distribución)
    - Estadísticas agregadas por nivel
    - Top 10 escenarios de mayor riesgo
    - Escenarios de riesgo alto sin plan de tratamiento
    """
    # Verificar acceso (multi-tenant + RBAC)
    analysis = await risk_service.get_analysis(
        analysis_id, corporate_id=current_user.corporate_id
    )

    if methodology == "fair":
        return await risk_service.get_fair_distribution(
            analysis_id,
            asset_type=asset_type
        )

    return await risk_service.get_qualitative_matrix(
        analysis_id,
        methodology=methodology,
        asset_type=asset_type,
        risk_level=risk_level
    )


@router.get("/analyses/{analysis_id}/untreated")
async def get_untreated_high_risks(
    analysis_id: int,
    current_user=Depends(get_current_user),
    risk_service: RiskService = Depends(),
):
    """Devuelve escenarios de riesgo alto o crítico sin plan de tratamiento.

    Este endpoint es el que más usan los auditores: identifica
    los riesgos que la organización ha evaluado como altos pero
    para los que no ha definido ninguna estrategia de mitigación.
    En una auditoría ENS, un riesgo alto sin tratamiento es una
    no conformidad.
    """
    return await risk_service.get_untreated_high_risks(
        analysis_id, corporate_id=current_user.corporate_id
    )
