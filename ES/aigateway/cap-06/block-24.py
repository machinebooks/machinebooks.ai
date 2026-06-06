# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
def is_content_policy_error(exc: Exception) -> bool:
    """Detecta filtros de contenido de distintos providers."""
    err = str(exc).lower()
    return any(needle in err for needle in (
        "content_filter", "content policy", "moderation",
        "safety_system", "blockedreason", "blocked content",
    ))
