# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/audited_client.py
import time
import hashlib
from dataclasses import dataclass

class AuditedLLMClient:
    """
    Envuelve cualquier cliente LLM y añade auditoría automática
    en cada llamada, sin que el servicio llamante deba hacer nada.
    """

    def __init__(self, inner, model_config, audit_service, request):
        self._inner = inner
        self._model = model_config
        self._audit = audit_service
        self._request = request

    def complete(self, messages: list, prompt_id: Optional[str] = None) -> str:
        start = time.monotonic()

        # Hash del prompt para verificación de integridad (compliance)
        prompt_hash = hashlib.sha256(
            str(messages).encode()
        ).hexdigest()[:16]

        try:
            response = self._inner.complete(messages)
            latency_ms = int((time.monotonic() - start) * 1000)

            # Registrar uso en LLMUsageLog
            self._audit.log_usage(
                service_type=self._request.service_type,
                provider=self._model.provider,
                model=self._model.model_id,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cost_eur=self._calculate_cost(response.usage),
                latency_ms=latency_ms,
                prompt_id=prompt_id,
                prompt_hash=prompt_hash,
                user_id=self._request.user_id,
                correlation_id=self._request.correlation_id
            )

            return response.content

        except Exception as e:
            self._audit.log_error(self._request, self._model, str(e))
            raise
