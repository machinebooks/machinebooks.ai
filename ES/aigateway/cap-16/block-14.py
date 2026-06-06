# Extraído de: LibroAIGateway/cap-16-jwt-device-binding.md
# Client fingerprint para session pinning (gateway/app/core/security.py:188-190)
def client_fingerprint(ip: str, user_agent: str) -> str:
    return hashlib.sha256(f"{ip}:{user_agent}".encode("utf-8")).hexdigest()
