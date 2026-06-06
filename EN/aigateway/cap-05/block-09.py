# Extracted from: LibroAIGateway/cap-05-router-smart-select.md
def _detach(cfg: LLMConfig | None, db: AsyncSession) -> LLMConfig | None:
    """Complete ORM detach so that any downstream mutation
    does NOT pollute the identity_map."""
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
