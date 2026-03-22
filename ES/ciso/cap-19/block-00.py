# Extraído de: LibroCISO/cap-19-dashboards-copiloto.md
# Ejemplo didáctico: endpoint de KPIs agregados para el CMI
from fastapi import APIRouter, Depends
from sqlalchemy import func, case
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/kpis")
async def get_dashboard_kpis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    corporate_id: int = Depends(get_tenant),  # Aislamiento multi-tenant
):
    """
    Agrega KPIs de privacidad, riesgo, cumplimiento y operaciones.
    Cada KPI tiene valor actual, valor anterior (para tendencia)
    y un umbral que determina el color (verde/amarillo/rojo).
    """
    # Privacidad: tratamientos sin DPIA cuando la necesitan
    treatments_needing_dpia = await db.execute(
        select(func.count())
        .where(Treatment.corporate_id == corporate_id)
        .where(Treatment.requires_dpia == True)
        .where(Treatment.dpia_status.in_(["pending", "not_started"]))
    )

    # Riesgo: riesgos con nivel alto/muy alto sin plan de tratamiento
    unmitigated_high_risks = await db.execute(
        select(func.count())
        .where(Risk.corporate_id == corporate_id)
        .where(Risk.inherent_level.in_(["high", "very_high"]))
        .where(Risk.treatment_plan_id == None)
    )

    # Cumplimiento: porcentaje de controles evaluados por marco
    controls_by_framework = await db.execute(
        select(
            Framework.name,
            func.count().label("total"),
            func.sum(
                case((ControlEvaluation.status == "evaluated", 1), else_=0)
            ).label("evaluated"),
        )
        .join(Control, Framework.id == Control.framework_id)
        .outerjoin(ControlEvaluation, Control.id == ControlEvaluation.control_id)
        .where(Framework.corporate_id == corporate_id)
        .group_by(Framework.name)
    )

    # Brechas: activas, notificadas a AEPD, fuera de plazo
    breach_stats = await db.execute(
        select(
            func.count().label("total_active"),
            func.sum(
                case((Breach.notified_to_authority == True, 1), else_=0)
            ).label("notified"),
            func.sum(case(
                (Breach.detected_at + timedelta(hours=72) < func.now(), 1),
                else_=0
            )).label("overdue"),
        )
        .where(Breach.corporate_id == corporate_id)
        .where(Breach.status == "active")
    )

    return DashboardKPIResponse(
        privacy=PrivacyKPIs(
            treatments_pending_dpia=treatments_needing_dpia.scalar(),
            # ... más KPIs de privacidad
        ),
        risk=RiskKPIs(
            unmitigated_high_risks=unmitigated_high_risks.scalar(),
            # ... más KPIs de riesgo
        ),
        compliance=ComplianceKPIs(
            frameworks=controls_by_framework.all(),
            # ... más KPIs de cumplimiento
        ),
        breaches=BreachKPIs(**breach_stats.first()._asdict()),
    )
