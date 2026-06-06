# Extraído de: LibroAIGateway/cap-07-adapters.md
OPENAI_ALLOWED_EXTRA = {
    "top_p", "frequency_penalty", "presence_penalty",
    "logit_bias", "stop", "user", "seed", "response_format",
}
def _filter_extra(extra: dict | None) -> dict:
    if not extra: return {}
    return {k: v for k, v in extra.items() if k in OPENAI_ALLOWED_EXTRA}
