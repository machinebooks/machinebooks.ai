# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/guardrail_service.py:120-126

def _safe_preview(match_text: str, category: str) -> str:
    """Si la categoría es PII, hasheamos en lugar de guardar clear text."""
    raw = (match_text or "")[:200]
    if category == "pii":
        return "sha256:" + hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]
    return raw
