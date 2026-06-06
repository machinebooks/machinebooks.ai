# Extraído de: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Canary token con sentinel HMAC-derived (leak_detection_service.py:239-252)
def _derive_sentinel(request_id: str) -> str:
    secret = settings.CANARY_HMAC_SECRET.encode()
    digest = hmac.new(secret, request_id.encode(), hashlib.sha256).digest()
    ZW = ["\u200b", "\u200c", "\u200d", "\ufeff"]  # 4 zero-width chars
    chars = []
    for byte in digest[:8]:
        chars.append(ZW[(byte >> 4) % 4])
        chars.append(ZW[byte % 4])
    return "".join(chars)
