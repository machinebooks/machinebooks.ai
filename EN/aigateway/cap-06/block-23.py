# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
@staticmethod
def is_model_allowed(config: LLMConfig, model_key: str) -> bool:
    if model_key == (config.model_name or ""):
        return True
    if (config.routing_mode or "fixed") != "auto":
        return False
    allowed = list(config.allowed_model_keys or [])
    if model_key in allowed:
        return True
    # Wildcard: 'gpt-5*' matches any model_key starting with gpt-5
    for pat in allowed:
        if fnmatch.fnmatchcase(model_key, pat):
            return True
    return False
