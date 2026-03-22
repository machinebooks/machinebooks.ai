# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
class PolicyAwarenessService:
    """Servicio principal de políticas y concienciación."""

    def __init__(self, db: AsyncSession, corporate_id: int):
        self.db = db
        self.corporate_id = corporate_id

    async def get_dashboard(self) -> dict:
        """Dashboard con métricas cruzadas de los tres ejes."""
        cid = self.corporate_id

        # Políticas por estado
        pol_q = await self.db.execute(
            select(
                SecurityPolicy.status,
                func.count(SecurityPolicy.id)
            ).where(
                SecurityPolicy.corporate_id == cid,
                SecurityPolicy.is_deleted == False
            ).group_by(SecurityPolicy.status)
        )
        policies_by_status = {r[0]: r[1] for r in pol_q.all()}
        total_policies = sum(policies_by_status.values())

        # Campañas activas
        active_campaigns = await self._count(
            AwarenessCampaign,
            AwarenessCampaign.status == CampaignStatus.ACTIVE
        )

        # Media de click rate en phishing
        avg_click_q = await self.db.execute(
            select(func.avg(PhishingSimulation.click_rate)).where(
                PhishingSimulation.corporate_id == cid,
                PhishingSimulation.is_deleted == False,
                PhishingSimulation.click_rate.isnot(None)
            )
        )
        avg_click_rate = avg_click_q.scalar()

        return {
            "total_policies": total_policies,
            "policies_by_status": policies_by_status,
            "active_campaigns": active_campaigns,
            "avg_phishing_click_rate": (
                round(avg_click_rate, 1) if avg_click_rate else None
            ),
        }
