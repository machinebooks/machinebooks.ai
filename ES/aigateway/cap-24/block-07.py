# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# request_id.py (sintético)
import uuid

def generate_request_id() -> str:
    return str(uuid.uuid4())

def get_request_id(request: Request) -> str:
    # Primero intenta leerlo del header (propagado desde upstream)
    rid = request.headers.get("X-N7x-Request-Id")
    if rid and len(rid) >= 32:
        return rid
    # Si no hay, genera uno nuevo
    return generate_request_id()
