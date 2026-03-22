# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
async def launch_campaign(
    self, campaign_id: int, user_id: int
) -> dict:
    """Lanza una campaña: planned → active."""
    camp = await self._get_campaign(campaign_id)
    if camp.status not in (CampaignStatus.PLANNED, "planned"):
        raise ValueError(
            f"Solo se pueden lanzar campañas en 'planned', "
            f"actual: {camp.status}"
        )
    camp.status = CampaignStatus.ACTIVE
    camp.start_date = camp.start_date or datetime.now(timezone.utc)
    await self.db.flush()
    return camp.to_dict()

async def complete_campaign(self, campaign_id: int) -> dict:
    """Cierra una campaña y recalcula estadísticas
    desde los registros individuales de completitud."""
    camp = await self._get_campaign(campaign_id)
    camp.status = CampaignStatus.COMPLETED
    camp.end_date = camp.end_date or datetime.now(timezone.utc)

    # Recalcular desde AwarenessCompletion
    comp_q = await self.db.execute(
        select(
            func.count(AwarenessCompletion.id),
            func.avg(AwarenessCompletion.score)
        ).where(
            AwarenessCompletion.campaign_id == campaign_id,
            AwarenessCompletion.is_deleted == False
        )
    )
    row = comp_q.one()
    camp.completed_count = row[0] or 0
    camp.pass_rate = round(float(row[1]), 1) if row[1] else None
    await self.db.flush()
    return camp.to_dict()
