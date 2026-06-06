# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
def _detach(cfg: LLMConfig | None, db: AsyncSession) -> LLMConfig | None:
    """Detach completo del ORM para que cualquier mutación aguas abajo
    NO contamine el identity_map."""
    if cfg is None:
        return None
    try:
        db.expunge(cfg)
    except Exception:
        pass
    try:
        make_transient(cfg)
    except Exception:
        pass
    return cfg
