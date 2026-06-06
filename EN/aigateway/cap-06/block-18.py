# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
def is_cooldownable_error(status_code, exc_class=None) -> tuple[bool, str]:
    """429 and 5xx yes. 4xx no (client problem)."""
    if status_code == 429:
        return True, "rate_limit"
    if status_code is not None and 500 <= status_code <= 599:
        return True, f"server_error_{status_code}"
    if exc_class and "timeout" in exc_class.lower():
        return True, "timeout"
    return False, ""
