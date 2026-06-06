# Extracted from: LibroAIGateway/cap-07-adapters.md
ADAPTER_MAP: dict[str, type[BaseLLMAdapter]] = {
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "azure": AzureAdapter,
    "azure_ai_inference": AzureAIInferenceAdapter,
    "bedrock": BedrockAdapter,
    "gemini": GeminiAdapter,
    "ollama": OllamaAdapter,
    "lmstudio": LMStudioAdapter,
}

def get_adapter(provider: str, extra_params: dict | None = None) -> BaseLLMAdapter:
    cls = ADAPTER_MAP.get((provider or "").strip().lower())
    if cls is None:
        raise ValueError(f"provider not supported: {provider}")
    extras = extra_params or {}
    endpoint = extras.get("endpoint")
    if endpoint:                       # SSRF guard on configurable endpoints
        validate_outbound_url(endpoint)
    return cls(**_kwargs_for(cls, extras))
