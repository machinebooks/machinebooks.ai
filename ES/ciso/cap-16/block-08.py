# Extraído de: LibroCISO/cap-16-rbac-multitenancy.md
class ReportingRepository:
    """Repositorio para queries de reporting y dashboards.

    Mantiene el filtro obligatorio por corporate_id pero permite
    queries con JOINs, agrupaciones y funciones de agregación.
    """

    def __init__(self, session: AsyncSession, corporate_id: int):
        self.session = session
        self.corporate_id = corporate_id

    async def get_risk_summary(self) -> dict:
        """Resumen de riesgos: conteo por nivel y estado de tratamiento."""
        query = (
            select(
                RiskAssessment.risk_level,
                func.count(RiskAssessment.id).label("count")
            )
            .where(RiskAssessment.corporate_id == self.corporate_id)
            .where(RiskAssessment.is_deleted == False)
            .group_by(RiskAssessment.risk_level)
        )
        result = await self.session.execute(query)
        return {row.risk_level: row.count for row in result.all()}

    async def get_compliance_dashboard(self) -> dict:
        """Dashboard de cumplimiento: porcentaje por marco regulatorio."""
        query = (
            select(
                Framework.name,
                func.count(Control.id).label("total_controls"),
                func.sum(
                    case((Control.status == "implemented", 1), else_=0)
                ).label("implemented")
            )
            .join(Control, Control.framework_id == Framework.id)
            .where(Framework.corporate_id == self.corporate_id)
            .where(Framework.is_deleted == False)
            .where(Control.is_deleted == False)
            .group_by(Framework.name)
        )
        result = await self.session.execute(query)
        return [
            {
                "framework": row.name,
                "total": row.total_controls,
                "implemented": row.implemented,
                "percentage": round(row.implemented / row.total_controls * 100, 1)
                if row.total_controls > 0 else 0
            }
            for row in result.all()
        ]
