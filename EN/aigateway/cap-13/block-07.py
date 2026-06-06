# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
def _compute_period(bucket: str, now: datetime) -> tuple[datetime, datetime]:
    if bucket == "session_5h":
        return now, now + timedelta(hours=5)          # Rolling from now
    if bucket == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)       # Midnight → midnight UTC
    if bucket == "weekly":
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return start, start + timedelta(days=7)       # Monday 00:00 → +7d
    if bucket == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # January → next month; December → year+1, month=1
        end = start.replace(year=start.year + (1 if start.month == 12 else 0),
                            month=(start.month % 12) + 1)
        return start, end
