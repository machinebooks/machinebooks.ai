# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
def is_cooldownable_error(status_code, exc_class=None) -> tuple[bool, str]:
    """429 y 5xx sí. 4xx no (problema del cliente)."""
    if status_code == 429:
        return True, "rate_limit"
    if status_code is not None and 500 <= status_code <= 599:
        return True, f"server_error_{status_code}"
    if exc_class and "timeout" in exc_class.lower():
        return True, "timeout"
    return False, ""
