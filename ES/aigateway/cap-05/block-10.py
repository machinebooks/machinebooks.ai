# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
@staticmethod
def is_model_allowed(config: LLMConfig, model_key: str) -> bool:
    if not model_key:                       # guard previo: vacío → denegar
        return False
    if model_key == (config.model_name or ""):
        return True
    if (config.routing_mode or "fixed") != "auto":
        return False
    allowed = list(config.allowed_model_keys or [])
    if model_key in allowed:
        return True
    # Solo se intenta fnmatch si el patrón tiene metacaracteres glob
    for pat in allowed:
        if any(c in pat for c in "*?[") and fnmatch.fnmatchcase(model_key, pat):
            return True
    return False
