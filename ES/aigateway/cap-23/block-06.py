# Extraído de: LibroAIGateway/cap-23-compliance-regulatorio.md
# gateway/app/services/dpo_service.py:41-43
def _pseudonym(email: str) -> str:
    raw = f"pseudonym:{email}{SALT}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
