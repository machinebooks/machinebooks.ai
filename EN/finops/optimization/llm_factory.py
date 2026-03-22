# Source: The FinOps Engineer and the Machine -- Chapter 10
# Pattern: Multi-provider LLM factory with cost tracking

# services/llm_factory.py
import anthropic
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import httpx
import logging

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """LLM providers available on the Platform."""
    LOCAL_OLLAMA   = "local_ollama"    # Local Ollama, token cost: $0
    LOCAL_VLLM     = "local_vllm"      # Local vLLM, high throughput
    ANTHROPIC_API  = "anthropic_api"   # Anthropic API, variable cost

@dataclass
class LLMRequest:
    """Normalized request, provider-independent."""
    system:     str
    user:       str
    max_tokens: int = 1024
    task_tier:  str = "balanced"   # fast | balanced | powerful

@dataclass
class LLMResponse:
    """Normalized response, provider-independent."""
    content:      str
    provider:     LLMProvider
    model:        str
    input_tokens: int
    output_tokens: int
    cost_usd:     float

# Tier-to-local-model map available in Ollama
LOCAL_MODEL_MAP = {
    "fast":     "qwen2.5:7b",      # extractions and classifications
    "balanced": "mistral-nemo",    # guided generation
    "powerful": None,              # no local model for powerful tier
}

# Tier-to-Anthropic-model map (fallback or primary)
ANTHROPIC_MODEL_MAP = {
    "fast":     "claude-haiku-4-5",
    "balanced": "claude-sonnet-4-6",
    "powerful": "claude-opus-4-6",
}

class LLMFactory:
    """
    LLM call factory with local → API fallback chain.
    Selects the provider based on task tier and availability.
    """

    # Providers to try in order (local first if available)
    FALLBACK_CHAIN = [
        LLMProvider.LOCAL_OLLAMA,
        LLMProvider.ANTHROPIC_API,
    ]

    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.anthropic_client = anthropic.Anthropic()
        self.ollama_url = ollama_base_url

    def _is_local_available(self, tier: str) -> bool:
        """Checks if a local model is available for this tier."""
        if LOCAL_MODEL_MAP.get(tier) is None:
            return False  # no local model for powerful tier

        try:
            # Ping the Ollama server with a short timeout
            resp = httpx.get(f"{self.ollama_url}/api/tags", timeout=1.0)
            return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    def _call_ollama(self, request: LLMRequest) -> LLMResponse:
        """Calls the local model via the Ollama API."""
        model = LOCAL_MODEL_MAP[request.task_tier]

        resp = httpx.post(
            f"{self.ollama_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": request.system},
                    {"role": "user",   "content": request.user},
                ],
                "stream": False,
                "options": {"num_predict": request.max_tokens},
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()

        return LLMResponse(
            content=      data["message"]["content"],
            provider=     LLMProvider.LOCAL_OLLAMA,
            model=        model,
            input_tokens= data.get("prompt_eval_count", 0),
            output_tokens=data.get("eval_count", 0),
            cost_usd=     0.0,  # local model: no token cost
        )

    def _call_anthropic(self, request: LLMRequest) -> LLMResponse:
        """Calls the Anthropic API with the model corresponding to the tier."""
        model = ANTHROPIC_MODEL_MAP[request.task_tier]

        msg = self.anthropic_client.messages.create(
            model=     model,
            max_tokens=request.max_tokens,
            system=    request.system,
            messages=  [{"role": "user", "content": request.user}],
        )

        input_t  = msg.usage.input_tokens
        output_t = msg.usage.output_tokens
        cost     = self._calculate_cost(model, input_t, output_t)

        return LLMResponse(
            content=      msg.content[0].text,
            provider=     LLMProvider.ANTHROPIC_API,
            model=        model,
            input_tokens= input_t,
            output_tokens=output_t,
            cost_usd=     cost,
        )

    def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Executes the LLM call with the configured fallback chain.
        Tries local first; if unavailable, uses the API.
        """
        for provider in self.FALLBACK_CHAIN:
            try:
                if provider == LLMProvider.LOCAL_OLLAMA:
                    if not self._is_local_available(request.task_tier):
                        continue  # skip; try the next in the chain
                    logger.info("Using local model for tier=%s", request.task_tier)
                    return self._call_ollama(request)

                elif provider == LLMProvider.ANTHROPIC_API:
                    logger.info("Using Anthropic API for tier=%s", request.task_tier)
                    return self._call_anthropic(request)

            except Exception as exc:
                logger.warning("Provider %s failed: %s; trying next", provider, exc)
                continue

        raise RuntimeError("All LLM providers failed")

    @staticmethod
    def _calculate_cost(model: str, input_t: int, output_t: int) -> float:
        """Calculates the USD cost of an Anthropic API call."""
        prices = {
            "claude-haiku-4-5":  (0.80, 4.00),
            "claude-sonnet-4-6": (3.00, 15.00),
            "claude-opus-4-6":   (15.00, 75.00),
        }
        inp_price, out_price = prices.get(model, (3.00, 15.00))
        return (input_t / 1_000_000 * inp_price
                + output_t / 1_000_000 * out_price)
