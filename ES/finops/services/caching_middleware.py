# Extraído de: LibroFinOps/cap-09-cache-prompt-batch.md
# services/caching_middleware.py
import anthropic
from typing import Optional

class CachingMiddleware:
    """
    Envuelve llamadas Anthropic añadiendo prompt caching
    en el system prompt y en documentos de referencia fijos.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()

    def create_with_cache(
        self,
        model: str,
        system: str,
        user_message: str,
        reference_docs: Optional[list[str]] = None,
        max_tokens: int = 1024,
    ) -> anthropic.types.Message:
        """
        Crea un mensaje con caching en system prompt y documentos fijos.

        El system prompt se marca como cacheable cuando tiene más de 200 palabras
        (aproximadamente 1.024 tokens o más).
        Los documentos de referencia (normas, plantillas) también se cachean.
        El user_message variable NO se cachea porque cambia en cada llamada.
        """

        # 1. Construir el system prompt con cache_control si es largo
        use_system_cache = len(system.split()) > 200

        # 2. Construir el mensaje de usuario
        user_content = []

        # Primero los documentos de referencia fijos (cacheables)
        # IMPORTANTE: el contenido cacheable debe ir ANTES del contenido variable
        if reference_docs:
            for doc in reference_docs:
                user_content.append({
                    "type": "text",
                    "text": doc,
                    "cache_control": {"type": "ephemeral"},
                })

        # Después el mensaje variable del usuario (no cacheable)
        user_content.append({
            "type": "text",
            "text": user_message,
            # Sin cache_control: este contenido cambia en cada llamada
        })

        # 3. Construir parámetros de la llamada
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user_content}],
        }

        if use_system_cache:
            kwargs["system"] = [{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }]
        else:
            kwargs["system"] = system

        return self.client.messages.create(**kwargs)

    def get_cache_stats(self, response: anthropic.types.Message) -> dict:
        """
        Extrae estadísticas de caché de la respuesta.
        Permite calcular el ahorro real por llamada para el LLMUsageLog.
        """
        usage = response.usage
        cache_read    = getattr(usage, "cache_read_input_tokens", 0)
        cache_created = getattr(usage, "cache_creation_input_tokens", 0)

        return {
            "input_tokens":          usage.input_tokens,
            "output_tokens":         usage.output_tokens,
            "cache_read_tokens":     cache_read,
            "cache_creation_tokens": cache_created,
            # Tokens facturados al precio de entrada normal
            "billed_normal_tokens":  usage.input_tokens - cache_read - cache_created,
        }
