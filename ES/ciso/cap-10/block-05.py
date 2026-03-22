# Extraído de: LibroCISO/cap-10-arquitectura-llm.md
from app.services.ai.llm_factory import LLMFactory
from app.extensions import get_db

def handle_ciso_question(question: str, user_id: str):
    """
    El CISO escribe una pregunta en el chat.
    El sistema usa el factory para enviarla al LLM configurado.
    """
    db = get_db()
    factory = LLMFactory(db)

    messages = [{"role": "user", "content": question}]

    try:
        # El factory consulta AIServiceConfig para "chat",
        # obtiene el proveedor (Anthropic), modelo (claude-sonnet-4-6),
        # temperatura (0.3), guardrails (pii_filter=true, injection_check=true),
        # y el prompt del sistema activo.
        result = factory.call(
            service_name="chat",
            messages=messages,
            user_id=user_id
        )

        if result.get("degraded_mode"):
            # El usuario debe saber que está en modo local
            return {
                "response": result["content"],
                "warning": "Sistema operando en modo local con capacidades reducidas. "
                          "Las respuestas pueden ser menos precisas que en modo normal.",
                "provider": result["provider"],
                "model": result["model"]
            }

        return {
            "response": result["content"],
            "provider": result["provider"],
            "model": result["model"],
            "tokens_used": result["input_tokens"] + result["output_tokens"]
        }

    except RuntimeError as e:
        # Todos los proveedores fallaron
        return {
            "error": "El servicio de IA no está disponible en este momento. "
                    "Las funcionalidades de consulta y generación están temporalmente "
                    "desactivadas. El resto de la Plataforma sigue operativa.",
            "details": str(e)
        }
