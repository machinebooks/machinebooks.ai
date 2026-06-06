# Extraído de: LibroAIGateway/cap-16-jwt-device-binding.md
# Verificación de device binding (gateway/app/core/security.py:260-284)
def enforce_device_binding(payload: dict | None, request) -> None:
    if not payload or not payload.get("device_id"):
        return  # Tokens legacy o service sin binding: no aplicar
    bound_device = payload["device_id"]
    header_device = request.headers.get("X-Device-ID", "") or ""
    if header_device != bound_device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="device_mismatch",
            headers={"WWW-Authenticate": "Bearer"},
        )
