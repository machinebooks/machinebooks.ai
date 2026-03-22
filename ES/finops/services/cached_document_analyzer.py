# Extraído de: LibroFinOps/cap-25-caso-tokens.md
# services/cached_document_analyzer.py
# Prompt caching de Anthropic para system prompts estáticos.
# Ahorro del 90% en tokens del system prompt cacheado.

import anthropic


class CachedDocumentAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def _system_prompt_legal(self) -> list[dict]:
        """System prompt para análisis legal. Se marca para cacheo."""
        return [{
            "type": "text",
            "text": """Eres un especialista en análisis documental legal
para el mercado español. Responde en el idioma del documento.
Si hay ambigüedad, indícala en "observaciones".
Formato JSON sin campos adicionales.
Fechas en ISO 8601. Importes en formato europeo.
No emitas juicios de valor sobre las partes.
No recomiendes acciones legales: solo describe riesgos.""",
            # Anthropic cachea este bloque: 10% del precio en lecturas
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
