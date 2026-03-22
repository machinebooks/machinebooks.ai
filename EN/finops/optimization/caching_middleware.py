# Source: The FinOps Engineer and the Machine -- Chapter 9
# Pattern: Anthropic caching middleware with cost tracking

# services/caching_middleware.py
import anthropic
from typing import Optional

class CachingMiddleware:
    """
    Wraps Anthropic calls adding prompt caching
    on the system prompt and on fixed reference documents.
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
        Creates a message with caching on the system prompt and fixed documents.

        The system prompt is marked as cacheable when it has more than 200 words
        (approximately 1,024 tokens or more).
        Reference documents (regulations, templates) are also cached.
        The variable user_message is NOT cached because it changes on every call.
        """

        # 1. Build the system prompt with cache_control if long enough
        use_system_cache = len(system.split()) > 200

        # 2. Build the user message
        user_content = []

        # First the fixed reference documents (cacheable)
        # IMPORTANT: cacheable content must go BEFORE variable content
        if reference_docs:
            for doc in reference_docs:
                user_content.append({
                    "type": "text",
                    "text": doc,
                    "cache_control": {"type": "ephemeral"},
                })

        # Then the variable user message (not cacheable)
        user_content.append({
            "type": "text",
            "text": user_message,
            # No cache_control: this content changes on every call
        })

        # 3. Build call parameters
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
        Extracts cache statistics from the response.
        Allows calculating the actual savings per call for the LLMUsageLog.
        """
        usage = response.usage
        cache_read    = getattr(usage, "cache_read_input_tokens", 0)
        cache_created = getattr(usage, "cache_creation_input_tokens", 0)

        return {
            "input_tokens":          usage.input_tokens,
            "output_tokens":         usage.output_tokens,
            "cache_read_tokens":     cache_read,
            "cache_creation_tokens": cache_created,
            # Tokens billed at the normal input price
            "billed_normal_tokens":  usage.input_tokens - cache_read - cache_created,
        }
