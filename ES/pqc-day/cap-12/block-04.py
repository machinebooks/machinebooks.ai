# Extraído de: LibroPQC/cap-12-agente-autonomo.md
def _call_ai_with_tools(self, messages: list) -> dict:
    """Enrutador multi-proveedor para llamadas con herramientas."""
    dispatch = {
        'anthropic': self._call_anthropic,
        'openai':    self._call_openai,
        'ollama':    self._call_ollama,
        'lmstudio':  self._call_lmstudio,
        'custom':    self._call_custom,  # vLLM, text-generation-inference
    }
    handler = dispatch.get(self.provider)
    if not handler:
        raise ValueError(f"Proveedor desconocido: {self.provider}")

    model = self.config.get('model', 'default')
    timeout = self.config.get('timeout', 120)
    return handler(messages, model, timeout)
