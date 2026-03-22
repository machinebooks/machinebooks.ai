# Extraído de: LibroFinOps/cap-10-selfhosted-vs-api.md
# En LLMFactory.complete(), después de obtener la respuesta:
async def _log_usage(self, response: LLMResponse, service: str):
    """Registra la llamada en el LLMUsageLog con el proveedor real."""
    await self.tracker.record(
        service=       service,
        model=         response.model,
        provider=      response.provider.value,
        input_tokens=  response.input_tokens,
        output_tokens= response.output_tokens,
        cost_usd=      response.cost_usd,
        # cost_usd=0.0 cuando el proveedor es local
        # Esto permite medir el "ahorro en tokens" del self-hosting
        # y cruzarlo con el TCO del hardware
    )
