# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/semantic_dedup_service.py:149-217 (sintetizado)
def build_semantic_hash(
    messages: list[dict],
    *, user_id: int | str | None, purpose: str | None,
    org_id: int | str | None = None,
    tool_result_fingerprint: str | None = None,
    model: str | None = None,
) -> Optional[str]:
    if user_id is None or not purpose:
        return None  # sin user_id no cacheamos (seguridad)
    # Extraer system + último user message
    # Normalizar → filtrar stopwords → ordenar tokens
    canonical = "|".join([
        model, org_id, str(user_id), purpose,
        tool_result_fingerprint,
        f"{length_bucket}:{' '.join(sorted(tokens))}",
    ])
    return hashlib.sha256(canonical.encode()).hexdigest()
