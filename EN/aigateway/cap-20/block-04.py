# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/content_classifier_service.py:175-191

@classmethod
async def classify_with_context(cls, messages: list[dict], ...) -> ClassificationResult:
    """Classifies the full context (all messages)."""
    user_text = " ".join(
        m.get("content", "")
        for m in messages
        if m.get("role") == "user" and m.get("content")
    )
    return await cls.classify(user_text, db, org_id, direction="input")
