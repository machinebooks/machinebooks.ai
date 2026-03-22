# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
async def submit_completion(
    self, campaign_id: int, data: dict, user_id: int
) -> dict:
    """Registra la completitud de una campaña por un usuario."""
    completion = AwarenessCompletion(
        corporate_id=self.corporate_id,
        campaign_id=campaign_id,
        user_id=data.get("user_id", user_id),
        user_email=data.get("user_email", ""),
        completed_at=datetime.now(timezone.utc),
        score=data.get("score"),
        # Aprobado si score >= passing_score (default 70)
        passed=(
            data.get("score", 0) >= data.get("passing_score", 70)
            if data.get("score") is not None else None
        ),
        attempts=data.get("attempts", 1),
        answers=data.get("answers"),
        created_by=user_id,
    )
    self.db.add(completion)
    await self.db.flush()

    # Actualizar estadísticas de la campaña
    await self._update_campaign_stats(campaign_id)
    return completion.to_dict()
