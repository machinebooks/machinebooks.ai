# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: middleware/request_id.py

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Garantiza que toda petición tenga un X-Request-ID único.

    Si el cliente (o Nginx) envía un X-Request-ID, se reutiliza.
    Si no, se genera uno nuevo. El ID se propaga a la respuesta
    y se almacena en request.state para uso en logs y audit.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Propagar ID existente o generar uno nuevo
        request_id = request.headers.get(
            "X-Request-ID", str(uuid.uuid4())
        )
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
