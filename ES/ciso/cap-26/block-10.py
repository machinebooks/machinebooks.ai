# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
async def get_compliance_evidence(self) -> dict:
    """Genera evidencia para auditoría de los controles
    de formación y concienciación."""
    return {
        "policies_published": await self._count_published_policies(),
        "campaigns_completed_last_year": await self._count_campaigns(
            status=CampaignStatus.COMPLETED,
            since=datetime.now(timezone.utc) - timedelta(days=365)
        ),
        "avg_completion_rate": await self._avg_completion_rate(),
        "avg_phishing_click_rate": await self._avg_click_rate(),
        "avg_culture_score": await self._avg_culture_score(),
        "evidence_generated_at": datetime.now(timezone.utc).isoformat(),
    }
