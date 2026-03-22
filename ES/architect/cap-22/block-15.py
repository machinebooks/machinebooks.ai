# Extraído de: LibroTecnico/cap-22-observabilidad.md
class NativeClientUsageTracker:
    """Wrapper para clientes nativos de Anthropic/OpenAI.
    Intercepta messages.create (Anthropic) o chat.completions.create (OpenAI)
    y reporta uso al backend sin bloquear la respuesta."""

    def __init__(self, client, model_name: str,
                 service_type: str, provider_type: str):
        self._client = client
        self._model_name = model_name
        self._service_type = service_type
        self._provider_type = provider_type
        # Contexto de negocio — se configura antes de cada llamada
        self._user_id: Optional[int] = None
        self._entity_type: Optional[str] = None  # "project", "client"
        self._entity_id: Optional[int] = None

        # Wrap Anthropic messages.create con tracking transparente
        if hasattr(client, 'messages') and hasattr(client.messages, 'create'):
            original = client.messages.create
            tracker = self

            @wraps(original)
            def tracked_create(*args, **kwargs):
                start = time.time()
                success = True
                try:
                    response = original(*args, **kwargs)
                    return response
                except Exception as e:
                    success = False
                    raise
                finally:
                    latency = int((time.time() - start) * 1000)
                    usage = {
                        'service_type': tracker._service_type,
                        'provider_type': tracker._provider_type,
                        'model_name': tracker._model_name,
                        'prompt_tokens': getattr(response.usage, 'input_tokens', 0)
                                         if success else 0,
                        'completion_tokens': getattr(response.usage, 'output_tokens', 0)
                                             if success else 0,
                        'latency_ms': latency,
                        'success': success,
                        'user_id': tracker._user_id,
                        'entity_type': tracker._entity_type,
                        'entity_id': tracker._entity_id,
                    }
                    tracker._report_async(usage)  # Fire & forget

            client.messages.create = tracked_create
