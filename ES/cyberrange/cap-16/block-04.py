# Extraído de: LibroCyberrange/cap-16-ia-por-que.md
# Servicio multi-proveedor de LLM
# Ejemplo didáctico: patrones/ia/llm_provider.py

from enum import Enum
from typing import Optional
import anthropic
import openai

class LLMProvider(str, Enum):
    CLAUDE = "claude"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"  # Modelos locales, sin conexión a internet

class LLMService:
    """Abstracción multi-proveedor para el Cyber Range."""

    def __init__(self, provider: LLMProvider, model: str, api_key: str = None):
        self.provider = provider
        self.model = model
        self._client = self._create_client(api_key)

    def _create_client(self, api_key):
        if self.provider == LLMProvider.CLAUDE:
            return anthropic.Anthropic(api_key=api_key)
        elif self.provider == LLMProvider.OPENAI:
            return openai.OpenAI(api_key=api_key)
        elif self.provider == LLMProvider.OLLAMA:
            return openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        # Azure OpenAI similar con endpoint personalizado

    def generate(self, system: str, prompt: str, max_tokens: int = 4096) -> str:
        if self.provider == LLMProvider.CLAUDE:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            # OpenAI y Ollama comparten la misma API
            response = self._client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
