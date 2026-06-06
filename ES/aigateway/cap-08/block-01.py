# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/services/cache_service.py:73-191 (sintetizado)
def build_query_hash(
    messages: list[dict],
    model: str,
    device_id: int | str | None = None,  # IGNORADO: no entra en la clave
    org_id: int | str | None = None,
    skill_command: str | None = None,
    user_id: int | str | None = None,
    tool_result_fingerprint: str | None = None,
    tools: list[dict] | None = None,
    reasoning_effort: str | None = None,
    response_format: dict | str | None = None,
) -> str | None:
    # IMPORTANTE: sin user_id, NO se cachea — previene leak cross-user
    if user_id is None or str(user_id).strip() == "":
        return None

    # 1. fingerprint del shape de tools (name + params, sin descripciones)
    tools_fp = _tools_shape_hash(tools)  # sha256 truncado a 16 hex

    # 2. fingerprint de response_format
    rf_fp = _response_format_hash(response_format)

    # 3. canónico: org + user + model + skill + tools + effort + rf + messages
    canonical = {
        "model": model.lower().strip(),
        "org_id": str(org_id) if org_id is not None else "",
        "user_id": str(user_id),
        "skill": (skill_command or "").strip(),
        "tool_fp": (tool_result_fingerprint or "").strip(),
        "tools_fp": tools_fp,
        "effort": (reasoning_effort or "").strip().lower(),
        "rf_fp": rf_fp,
        "messages": [
            {"role": m["role"], "content": _content_text(m.get("content"))}
            for m in messages if _content_text(m.get("content"))
        ],
    }
    payload = "|".join([
        canonical["org_id"], canonical["user_id"],
        canonical["model"], canonical["skill"],
        canonical["tool_fp"], canonical["tools_fp"],
        canonical["effort"], canonical["rf_fp"],
        json.dumps(canonical["messages"], sort_keys=True),
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
