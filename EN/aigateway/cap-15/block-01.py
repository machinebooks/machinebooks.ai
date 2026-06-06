# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
# gateway/app/core/rate_limit.py:51-72
def _get_rate_limit_key(request) -> str:
    """Hierarchical rate limit key: user_id > device_id > IP."""
    user_key = _get_user_id_from_jwt(request)
    if user_key:
        return user_key  # "user:<uuid>"

    device_id = request.headers.get("X-Device-ID", "")
    if device_id and _DEVICE_ID_RE.match(device_id):
        return f"dev:{device_id}"

    return f"ip:{get_remote_address(request)}"  # last resort
