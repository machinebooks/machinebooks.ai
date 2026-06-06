# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/content_classifier_service.py:175-191

@classmethod
async def classify_with_context(cls, messages: list[dict], ...) -> ClassificationResult:
    """Clasifica el contexto completo (todos los mensajes)."""
    user_text = " ".join(
        m.get("content", "")
        for m in messages
        if m.get("role") == "user" and m.get("content")
    )
    return await cls.classify(user_text, db, org_id, direction="input")
