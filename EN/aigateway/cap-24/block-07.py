# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# request_id.py (synthetic)
import uuid

def generate_request_id() -> str:
    return str(uuid.uuid4())

def get_request_id(request: Request) -> str:
    # First tries to read it from the header (propagated from upstream)
    rid = request.headers.get("X-N7x-Request-Id")
    if rid and len(rid) >= 32:
        return rid
    # If not present, generates a new one
    return generate_request_id()
