# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
async def acquire(
    db: AsyncSession,
    *,
    user_id: int | None = None,
    team_id: int | None = None,
    organization_id: int | None = None,
    device_id: str | None = None,
) -> list[str]:
    """Reserves RPM + parallel slot for the scopes that have a limit.
    Raises RateLimitExceeded on the first one that exceeds the cap.
    Returns the list of scopes acquired (for release() in finally)."""
