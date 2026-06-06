# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# gateway/app/middleware/json_logging.py: sanitizer
_SECRET_HEADERS = {"authorization", "x-api-key", "cookie", "x-n7x-device-fingerprint"}

def _sanitize_headers(headers: Headers) -> dict[str, str]:
    result = {}
    for name, value in headers.items():
        if name.lower() in _SECRET_HEADERS:
            result[name] = "***REDACTED***"
        else:
            result[name] = value
    return result
