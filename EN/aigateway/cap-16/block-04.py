# Extracted from: LibroAIGateway/cap-16-jwt-device-binding.md
# The same calculation as in the TypeScript extension (gateway/app/core/security.py)
def hash_device_id(machine_id: str, hostname: str,
                   username: str, org_id: str) -> str:
    raw = f"{machine_id}:{hostname}:{username}:{org_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
