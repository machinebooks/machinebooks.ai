# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
async def get_timeline(self, days: int = 90) -> list[dict]:
    """Actualizaciones recientes ordenadas cronológicamente.

    Parámetro days configurable: 90 para informes trimestrales,
    30 para seguimiento mensual, 365 para revisión anual.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await self.db.execute(
        select(RegulatoryUpdate).where(
            RegulatoryUpdate.corporate_id == self.corporate_id,
            RegulatoryUpdate.is_deleted == False,
            RegulatoryUpdate.created_at >= cutoff,
        ).order_by(RegulatoryUpdate.created_at.desc())
        .limit(100)
    )
    return [u.to_dict() for u in result.scalars().all()]
