# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/guardrail_service.py:120-126

def _safe_preview(match_text: str, category: str) -> str:
    """If the category is PII, we hash instead of storing clear text."""
    raw = (match_text or "")[:200]
    if category == "pii":
        return "sha256:" + hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]
    return raw
