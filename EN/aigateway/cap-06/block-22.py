# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
def classify_trigger(exc: Exception) -> str | None:
    """We only escalate for transient provider errors."""
    if "timeout" in str(exc).lower():
        return "timeout"
    for code in ("500", "502", "503", "504"):
        if code in str(exc).lower():
            return code
    if "429" in err_str and ("drained" in err_str or "all" in err_str):
        return "429_all_drained"
    return None  # 4xx are not escalated
