"""
Chapter 11: LLM Factory — multi-provider abstraction with fallback chains.

The Factory pattern decouples AI services from specific providers:
  - Primary: Anthropic (Claude) — claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5
  - Fallback: Azure OpenAI, OpenAI direct, Ollama (local)
  - Selection policy: privacy > availability > cost

Key features:
  - Budget check before every call (BudgetService)
  - Automatic audit of every invocation (AuditedLLMClient wrapper)
  - Multi-level cache: config (60s), prompts (30s agents / 300s stable), LLM instances
  - Failover logging and circuit breaker per provider
  - Native client tracking for non-LangChain calls (Agent SDK)
"""

import enum
import hashlib
import time
from dataclasses import dataclass
from typing import Optional, List


# =============================================================================
# Provider enum (Chapter 11)
# =============================================================================

class LLMProvider(enum.Enum):
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    AZURE_AI_FOUNDRY = "azure_ai_foundry"  # Claude via Azure infrastructure


@dataclass
class LLMRequest:
    """Request context passed to the factory."""
    service_type: str           # e.g. "document_analysis", "proposal_generation"
    user_id: Optional[int] = None
    task_complexity: str = "standard"  # "simple", "standard", "complex"
    requires_local: bool = False       # True = privacy restriction, local only
    correlation_id: Optional[str] = None


@dataclass
class ModelConfig:
    """Resolved model configuration from LLMServiceConfig."""
    provider: LLMProvider
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 4096


# =============================================================================
# LLM Factory (Chapter 11)
# =============================================================================

class LLMFactory:
    """
    Central factory for LLM clients.
    Decouples AI services from the specific provider.

    Usage:
        factory = LLMFactory(config_service, budget_service, audit_service)
        client = factory.get_client(LLMRequest(service_type="document_analysis"))
        response = client.complete(messages=[...])
    """

    def __init__(self, config_service, budget_service, audit_service):
        self._config = config_service   # Reads LLMServiceConfig from DB
        self._budget = budget_service   # Checks spending limits
        self._audit = audit_service     # Logs every call

    def get_client(self, request: LLMRequest) -> "AuditedLLMClient":
        """
        Return the correct client based on active policies.
        Raises ProviderUnavailableError if no provider can serve the request.
        """
        # 1. Check budget before building the client
        self._budget.check_or_raise(request.user_id, request.service_type)

        # 2. Select provider based on policies
        provider = self._select_provider(request)

        # 3. Build client with appropriate model
        model_config = self._config.get_model_config(
            provider, request.task_complexity
        )

        # 4. Wrap in audited client (every call is tracked automatically)
        return AuditedLLMClient(
            inner=self._build_inner_client(provider, model_config),
            model_config=model_config,
            audit_service=self._audit,
            request=request,
        )

    def _select_provider(self, request: LLMRequest) -> LLMProvider:
        """
        Provider selection policy: privacy > availability > cost.

        If requires_local is True (privacy restriction), only local inference
        (Ollama) is allowed — cloud providers are excluded.
        """
        if request.requires_local:
            return LLMProvider.OLLAMA

        primary = self._config.get_primary_provider(request.service_type)

        if self._is_available(primary):
            return primary

        # Automatic failover: select next available provider
        for fallback in self._config.get_fallback_providers(primary):
            if self._is_available(fallback):
                self._audit.log_failover(request, primary, fallback)
                return fallback

        raise ProviderUnavailableError(
            f"No provider available for {request.service_type}"
        )

    def _is_available(self, provider: LLMProvider) -> bool:
        """Check provider availability via circuit breaker state."""
        # In production: check circuit breaker in Redis
        # key = f"circuit:{provider.value}"
        # state = redis_client.get(key)
        # return state != "open"
        return True

    def _build_inner_client(self, provider: LLMProvider, config: ModelConfig):
        """Build the actual LLM client (LangChain or native)."""
        # In production: returns ChatAnthropic, AzureChatOpenAI, etc.
        pass


# =============================================================================
# AuditedLLMClient (Chapter 11)
# =============================================================================

class AuditedLLMClient:
    """
    Wraps any LLM client and adds automatic audit on every call.
    The calling service does not need to do anything — audit is transparent.

    Every invocation is logged to LLMUsageLog with:
      - tokens (input + output)
      - cost in EUR (calculated from LLMModelPricing)
      - latency in milliseconds
      - prompt hash for traceability without storing sensitive content
    """

    def __init__(self, inner, model_config, audit_service, request):
        self._inner = inner
        self._model = model_config
        self._audit = audit_service
        self._request = request

    def complete(self, messages: list, prompt_id: Optional[str] = None) -> str:
        """Send messages to the LLM with automatic audit."""
        start = time.monotonic()

        # Hash prompt for traceability (compliance)
        prompt_hash = hashlib.sha256(
            str(messages).encode()
        ).hexdigest()[:16]

        try:
            response = self._inner.complete(messages)
            latency_ms = int((time.monotonic() - start) * 1000)

            # Log to LLMUsageLog
            self._audit.log_usage(
                service_type=self._request.service_type,
                provider=self._model.provider.value,
                model=self._model.model_id,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cost_eur=self._calculate_cost(response.usage),
                latency_ms=latency_ms,
                prompt_id=prompt_id,
                prompt_hash=prompt_hash,
                user_id=self._request.user_id,
                correlation_id=self._request.correlation_id,
            )

            return response.content

        except Exception as e:
            self._audit.log_error(self._request, self._model, str(e))
            raise

    def _calculate_cost(self, usage) -> float:
        """Calculate cost in EUR using LLMModelPricing table."""
        # In production: fetch active pricing from cache/DB
        # pricing = pricing_cache.get(self._model.provider, self._model.model_id)
        # cost = (usage.input_tokens / 1000 * pricing.input_price_per_1k +
        #         usage.output_tokens / 1000 * pricing.output_price_per_1k)
        return 0.0


# =============================================================================
# Multi-level cache (Chapter 11)
# =============================================================================

_config_cache: dict = {}
_config_cache_ts: float = 0
_prompt_cache: dict = {}
_prompt_cache_timestamps: dict = {}


def get_service_config(service_type: str) -> Optional[dict]:
    """
    Get AI service config with 60-second in-memory cache.

    Chapter 11: In-memory cache (~1us access) over Redis (~1ms) because
    AI config changes rarely (order of times per day, not per second).
    The 60-second inconsistency between replicas is acceptable vs
    the complexity of distributed cache invalidation.
    """
    global _config_cache, _config_cache_ts

    if time.time() - _config_cache_ts < 60 and service_type in _config_cache:
        return _config_cache[service_type]

    # HTTP call to backend (only every 60s per service)
    data = _fetch_config_from_backend(service_type)
    if data:
        _config_cache[service_type] = data
        _config_cache_ts = time.time()
    return data


def get_prompt(prompt_key: str, default: str = "") -> str:
    """
    Get prompt from DB config with differentiated TTL:
      - agent.* -> 30s (frequent changes during development)
      - rest    -> 300s (stable in production)
    """
    cache_ttl = 30 if prompt_key.startswith("agent.") else 300

    if prompt_key in _prompt_cache:
        entry_ts = _prompt_cache_timestamps.get(prompt_key, 0)
        if time.time() - entry_ts < cache_ttl:
            return _prompt_cache[prompt_key]

    prompt_text = _fetch_prompt_from_backend(prompt_key)
    if prompt_text:
        _prompt_cache[prompt_key] = prompt_text
        _prompt_cache_timestamps[prompt_key] = time.time()
        return prompt_text

    return default


# =============================================================================
# Helpers (stubs for didactic purposes)
# =============================================================================

def _fetch_config_from_backend(service_type: str) -> Optional[dict]:
    """In production: HTTP GET to backend /api/ai-config/{service_type}"""
    return None


def _fetch_prompt_from_backend(prompt_key: str) -> Optional[str]:
    """In production: HTTP GET to backend /api/ai-config/prompts/{key}"""
    return None


class ProviderUnavailableError(Exception):
    pass
