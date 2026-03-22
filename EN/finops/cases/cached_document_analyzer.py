# Source: The FinOps Engineer and the Machine -- Chapter 25
# Pattern: Document analyzer with semantic caching

# services/cached_document_analyzer.py
# Anthropic prompt caching for static system prompts.
# 90% savings on tokens from the cached system prompt.

import anthropic


class CachedDocumentAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def _system_prompt_legal(self) -> list[dict]:
        """System prompt for legal analysis. Marked for caching."""
        return [{
            "type": "text",
            "text": """You are a specialist in legal document analysis
for the Spanish market. Respond in the document's language.
If there is ambiguity, indicate it in "observations".
JSON format without additional fields.
Dates in ISO 8601. Amounts in European format.
Do not make value judgments about the parties.
Do not recommend legal actions: only describe risks.""",
            # Anthropic caches this block: 10% of the price on reads
            "cache_control": {"type": "ephemeral"},
        }]

    async def analizar(self, texto: str, operacion: str, modelo: str) -> dict:
        response = self.client.messages.create(
            model=modelo,
            max_tokens=2048,
            system=self._system_prompt_legal(),
            messages=[{"role": "user", "content": texto[:12000]}],
        )
        uso = response.usage
        return {
            "resultado": response.content[0].text,
            "cache_hit": getattr(uso, "cache_read_input_tokens", 0) > 0,
            "tokens_cacheados": getattr(uso, "cache_read_input_tokens", 0),
        }
