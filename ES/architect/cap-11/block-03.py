# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico basado en: ai_service/services/llm_usage_tracker.py
import time
import threading
from functools import wraps

class NativeClientUsageTracker:
    """
    Wrapper para clientes nativos (no LangChain).
    Intercepta messages.create (Anthropic) o chat.completions.create (OpenAI)
    y reporta uso al backend de forma asíncrona (fire & forget).
    """

    def __init__(self, client, model_name: str, service_type: str, provider_type: str):
        self._client = client
        self._model_name = model_name
        self._service_type = service_type
        self._provider_type = provider_type

        # Detectar tipo de cliente e interceptar el método correcto
        if hasattr(client, 'messages') and hasattr(client.messages, 'create'):
            # Cliente Anthropic nativo
            original = client.messages.create

            @wraps(original)
            def tracked_create(*args, **kwargs):
                start = time.time()
                try:
                    response = original(*args, **kwargs)
                    latency = int((time.time() - start) * 1000)
                    usage = {
                        'service_type': self._service_type,
                        'provider_type': self._provider_type,
                        'model_name': getattr(response, 'model', model_name),
                        'prompt_tokens': getattr(response.usage, 'input_tokens', 0),
                        'completion_tokens': getattr(response.usage, 'output_tokens', 0),
                        'latency_ms': latency,
                        'success': True,
                    }
                    self._report_async(usage)
                    return response
                except Exception as e:
                    self._report_async({'success': False, 'error_type': type(e).__name__})
                    raise

            client.messages.create = tracked_create

    def __getattr__(self, name):
        """Proxy transparente: todo lo no definido se delega al cliente real."""
        return getattr(self._client, name)

    def _report_async(self, usage_data: dict):
        """Fire & forget: reporta al backend en un thread daemon."""
        def _send():
            # POST a /ai-metrics/usage (no bloquea el hilo principal)
            ...
        threading.Thread(target=_send, daemon=True).start()
