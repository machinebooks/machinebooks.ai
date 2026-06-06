# Extraído de: LibroAIGateway/cap-13-tenants-cuotas.md
def _compute_period(bucket: str, now: datetime) -> tuple[datetime, datetime]:
    if bucket == "session_5h":
        return now, now + timedelta(hours=5)          # Rolling desde ahora
    if bucket == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)       # Medianoche → medianoche UTC
    if bucket == "weekly":
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return start, start + timedelta(days=7)       # Lunes 00:00 → +7d
    if bucket == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Enero → siguiente mes; diciembre → año+1, mes=1
        end = start.replace(year=start.year + (1 if start.month == 12 else 0),
                            month=(start.month % 12) + 1)
        return start, end
