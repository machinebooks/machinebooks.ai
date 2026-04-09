# Extracted from: LibroAISafety/ch-19-observability.md
import hashlib
import re
import time
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware, RequestResponseEndpoint
)
import logging

logger = logging.getLogger("ai_security")

class AISecurityMiddleware(BaseHTTPMiddleware):
    """Middleware that monitors security of AI interactions."""

    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?previous",
        r"(?i)you\s+are\s+now",
        r"(?i)system\s*:\s*",
        r"(?i)new\s+instructions",
        r"(?i)override\s+(your|the)",
        r"(?i)DAN\s+mode",
        r"(?i)jailbreak",
    ]

    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone_es": r"\+?34[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}",
        "dni": r"\d{8}[A-Z]",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    }

    def __init__(self, app, system_prompt: str = ""):
        super().__init__(app)
        self.system_prompt_hash = hashlib.sha256(
            system_prompt.encode()
        ).hexdigest()
        system_prompt_hash.info({
            "hash": self.system_prompt_hash,
            "length": str(len(system_prompt)),
        })

    async def dispatch(self, request: Request,
                       call_next: RequestResponseEndpoint
                       ) -> Response:
        """Intercepts requests and records security metrics."""
        if not request.url.path.startswith("/api/ai/"):
            return await call_next(request)

        start_time = time.monotonic()

        # Read request body
        body = await request.body()
        prompt_text = body.decode("utf-8", errors="replace")

        # 1. Detect injection in the prompt
        injection_severity = self._detect_injection(prompt_text)
        if injection_severity:
            injection_attempts.labels(
                severity=injection_severity,
                user_type="authenticated",
                detection_method="pattern"
            ).inc()
            logger.warning(
                f"Injection detected [{injection_severity}]: "
                f"user={request.headers.get('X-User-ID', '?')}"
            )

        # 2. Process the request
        response = await call_next(request)

        # 3. Record latency
        duration = time.monotonic() - start_time
        generation_latency.observe(duration)

        # 4. Record response length
        # (requires access to response body)
        content_length = response.headers.get("content-length", "0")
        response_length.observe(int(content_length))

        return response

    def _detect_injection(self, text: str) -> Optional[str]:
        """Classifies the detected injection level."""
        matches = sum(
            1 for p in self.INJECTION_PATTERNS
            if re.search(p, text)
        )
        if matches >= 3:
            return "high"
        elif matches >= 2:
            return "medium"
        elif matches >= 1:
            return "low"
        return None

    def check_pii_in_response(self, response_text: str) -> list[str]:
        """Detects PII in the model's response."""
        found_pii = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, response_text):
                found_pii.append(pii_type)
                pii_detections.labels(pii_type=pii_type).inc()
        return found_pii
