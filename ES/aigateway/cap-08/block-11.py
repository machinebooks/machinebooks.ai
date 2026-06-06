# Extraído de: LibroAIGateway/cap-08-caching.md
# gateway/app/adapters/openai_adapter.py:23-87 (sintetizado)
def _compute_prompt_cache_key(messages: list[dict],
                              tools: list[dict] | None = None,
                              min_chars: int = 800) -> str | None:
    # Recolectar prefijo invariante: system + developer al inicio
    prefix_parts = []
    for m in messages:
        role = m.get("role")
        if role not in ("system", "developer"):
            break  # user/assistant cambian cada turn, no son invariantes
        content = _extract_text(m.get("content"))
        if content:
            prefix_parts.append(f"{role}:{content}")

    # Anexar shape de tools (name + params, sin descripciones)
    if tools:
        shapes = [{"name": t["name"], "params": t.get("parameters") or {}}
                  for t in tools if isinstance(t, dict)]
        prefix_parts.append("tools:" + json.dumps(shapes, sort_keys=True))

    if not prefix_parts:
        return None
    prefix = "\n".join(prefix_parts)
    if len(prefix) < min_chars:
        return None  # prefijo corto: OpenAI ya cachea automaticamente
    return hashlib.sha256(prefix.encode("utf-8")).hexdigest()[:40]
