# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
class LLMUsageTracker:
    """Wrapper transparente alrededor de un LLM de LangChain.
    Intercepta invoke/ainvoke, extrae tokens de usage_metadata,
    y reporta el uso al backend sin modificar la interfaz del LLM."""

    def __init__(self, llm, service_type, provider_type, model_name):
        self._llm = llm
        self._service_type = service_type       # Ej: "document_analyzer"
        self._provider_type = provider_type     # Ej: "anthropic"
        self._model_name = self._resolve_model_name(llm, model_name)
        self._user_id: Optional[int] = None
        self._entity_type: Optional[str] = None
        self._entity_id: Optional[int] = None
