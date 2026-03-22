# Chapter 10 — LLMFactory with 3-level fallback
#
# Creates LLM clients dynamically from database configuration.
# Fallback chain: Anthropic (cloud) -> Azure OpenAI (cloud alt) -> Ollama (local).
# Every call is tracked: provider, model, tokens, latency, cost.

import time
import logging
from typing import Optional
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# Client cache with TTL to avoid creating connections on every call
_client_cache: dict[str, tuple[object, datetime]] = {}
_CACHE_TTL = timedelta(minutes=10)


class LLMFactory:
    """Factory that creates LLM clients dynamically from DB configuration.

    Usage:
        factory = LLMFactory(db_session)
        result = factory.call(
            service_name="privacy_agent",
            messages=[{"role": "user", "content": "Analyze treatment X"}],
        )
        print(result["content"])
        print(f"Cost: {result['cost_eur']:.4f} EUR")
    """

    def __init__(self, db_session):
        self.db = db_session

    def get_service_config(self, service_name: str):
        """Load active configuration for a service from the database."""
        # In production: query AIServiceConfig with joins to AIProvider and AIPrompt
        # Here we show the pattern — the actual ORM query depends on your setup.
        from backend.models.ai import AIServiceConfig
        config = self.db.query(AIServiceConfig).filter(
            AIServiceConfig.service_name == service_name,
            AIServiceConfig.is_active == True,
        ).first()
        if not config:
            raise ValueError(f"AI service '{service_name}' not configured or inactive")
        return config

    def _create_client(self, provider):
        """Create or retrieve a cached client for the given provider."""
        cache_key = f"{provider.name}_{provider.id}"
        now = datetime.now(timezone.utc)

        if cache_key in _client_cache:
            client, cached_at = _client_cache[cache_key]
            if now - cached_at < _CACHE_TTL:
                return client

        # Retrieve API key from vault (never stored in plain text)
        api_key = self._get_api_key(provider.api_key_ref) if provider.api_key_ref else None

        from backend.models.ai import ProviderType
        import anthropic
        import openai

        if provider.provider_type == ProviderType.ANTHROPIC:
            client = anthropic.Anthropic(api_key=api_key)

        elif provider.provider_type == ProviderType.OPENAI:
            client = openai.OpenAI(api_key=api_key)

        elif provider.provider_type == ProviderType.AZURE_OPENAI:
            client = openai.AzureOpenAI(
                api_key=api_key,
                azure_endpoint=provider.api_base_url,
                api_version="2024-06-01",
            )

        elif provider.provider_type == ProviderType.OLLAMA:
            # Ollama exposes an OpenAI-compatible API
            client = openai.OpenAI(
                base_url=provider.api_base_url or "http://ollama:11434/v1",
                api_key="ollama",  # Ollama does not require a real key
            )

        elif provider.provider_type == ProviderType.LM_STUDIO:
            client = openai.OpenAI(
                base_url=provider.api_base_url or "http://lm-studio:1234/v1",
                api_key="lm-studio",
            )
        else:
            raise ValueError(f"Unsupported provider type: {provider.provider_type}")

        _client_cache[cache_key] = (client, now)
        return client

    def _call_provider(self, provider, model_name: str, messages: list[dict],
                       config, system_prompt: Optional[str] = None) -> dict:
        """Execute a call to a specific provider with cost tracking."""
        from backend.models.ai import ProviderType
        client = self._create_client(provider)
        start_time = time.time()

        try:
            if provider.provider_type == ProviderType.ANTHROPIC:
                response = client.messages.create(
                    model=model_name,
                    max_tokens=config.max_output_tokens,
                    temperature=config.temperature,
                    system=system_prompt or "",
                    messages=messages,
                )
                content = response.content[0].text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
            else:
                # OpenAI-compatible API (OpenAI, Azure, Ollama, LM Studio)
                full_messages = []
                if system_prompt:
                    full_messages.append({"role": "system", "content": system_prompt})
                full_messages.extend(messages)

                response = client.chat.completions.create(
                    model=model_name,
                    max_tokens=config.max_output_tokens,
                    temperature=config.temperature,
                    messages=full_messages,
                )
                content = response.choices[0].message.content
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            latency_ms = int((time.time() - start_time) * 1000)

            # Calculate estimated cost from provider pricing
            cost_eur = self._estimate_cost(provider, model_name, input_tokens, output_tokens)

            return {
                "content": content,
                "provider": provider.name,
                "model": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "cost_eur": cost_eur,
                "fallback_used": False,
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.warning(
                f"Error in provider {provider.name}/{model_name}: {e} "
                f"(latency: {latency_ms}ms)"
            )
            raise

    def call(self, service_name: str, messages: list[dict],
             system_prompt: Optional[str] = None) -> dict:
        """Main entry point. Calls the configured provider with automatic fallback.

        Fallback chain: primary -> fallback_level_1 -> local_fallback
        """
        config = self.get_service_config(service_name)

        # Resolve system prompt from DB if not provided
        if system_prompt is None and config.active_prompt:
            system_prompt = config.active_prompt.prompt_text

        # Attempt primary provider
        try:
            return self._call_provider(
                provider=config.provider,
                model_name=config.model_name,
                messages=messages,
                config=config,
                system_prompt=system_prompt,
            )
        except Exception as primary_error:
            logger.warning(f"Primary provider failed for {service_name}: {primary_error}")

        # Attempt fallback level 1 (secondary cloud)
        if config.fallback_provider_id:
            try:
                fallback_provider = self.db.get(
                    type(config.provider), config.fallback_provider_id
                )
                result = self._call_provider(
                    provider=fallback_provider,
                    model_name=config.fallback_model_name,
                    messages=messages,
                    config=config,
                    system_prompt=system_prompt,
                )
                result["fallback_used"] = True
                return result
            except Exception as fallback_error:
                logger.warning(f"Fallback L1 failed for {service_name}: {fallback_error}")

        # Attempt fallback level 2 (local — Ollama)
        if config.local_fallback_provider_id:
            try:
                local_provider = self.db.get(
                    type(config.provider), config.local_fallback_provider_id
                )
                result = self._call_provider(
                    provider=local_provider,
                    model_name=config.local_fallback_model_name,
                    messages=messages,
                    config=config,
                    system_prompt=system_prompt,
                )
                result["fallback_used"] = True
                result["degraded_mode"] = True  # Signal reduced quality
                return result
            except Exception as local_error:
                logger.error(f"All providers failed for {service_name}: {local_error}")

        raise RuntimeError(
            f"All AI providers exhausted for service '{service_name}'. "
            "Check provider health and network connectivity."
        )

    def _estimate_cost(self, provider, model_name: str,
                       input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in EUR from provider pricing stored in DB."""
        if not provider.available_models:
            return 0.0
        for model_info in provider.available_models:
            if model_info.get("name") == model_name:
                input_cost = (input_tokens / 1_000_000) * model_info.get("input_price", 0)
                output_cost = (output_tokens / 1_000_000) * model_info.get("output_price", 0)
                return round(input_cost + output_cost, 6)
        return 0.0

    @staticmethod
    def _get_api_key(key_ref: str) -> str:
        """Retrieve API key from secure vault.
        In production: HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault.
        """
        import os
        # Simplified: read from environment variable matching the ref
        return os.environ.get(key_ref, "<YOUR_API_KEY>")
