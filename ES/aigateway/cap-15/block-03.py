# Extraído de: LibroAIGateway/cap-15-rate-limiting.md
async def acquire(
    db: AsyncSession,
    *,
    user_id: int | None = None,
    team_id: int | None = None,
    organization_id: int | None = None,
    device_id: str | None = None,
) -> list[str]:
    """Reserva slot RPM + parallel para los scopes que tengan límite.
    Lanza RateLimitExceeded en el primero que supere el cap.
    Devuelve la lista de scopes acquired (para release() en finally)."""
