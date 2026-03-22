# Source: The FinOps Engineer and the Machine -- Chapter 25
# Pattern: Intelligent context truncation

# services/context_truncator.py
# Intelligent truncation: sends only what the model needs.
# Average 30% reduction in input tokens.

class ContextTruncator:
    """
    Strategy by operation:
    - Classification: 500 tokens (header)
    - Extraction: 8,000 tokens (entities at the beginning)
    - Summary: start + end (sandwich)
    - Recommendation: header + relevant clauses
    """
    MAX_TOKENS = {
        "clasificacion": 500,
        "extraccion_entidades": 8_000,
        "resumen_ejecutivo": 12_000,
        "recomendacion_accion": 10_000,
    }
    CHARS_POR_TOKEN = 4  # Approximation for Spanish

    def truncar(self, texto: str, operacion: str) -> tuple[str, dict]:
        max_chars = self.MAX_TOKENS.get(operacion, 8_000) * self.CHARS_POR_TOKEN
        tokens_orig = len(texto) // self.CHARS_POR_TOKEN

        if len(texto) <= max_chars:
            return texto, {"truncado": False, "ratio": 1.0}

        if operacion == "resumen_ejecutivo":
            # Sandwich: 65% inicio + 30% final
            inicio = texto[:int(max_chars * 0.65)]
            fin = texto[-int(max_chars * 0.30):]
            truncado = inicio + "\n\n[...]\n\n" + fin
        else:
            truncado = texto[:max_chars]

        return truncado, {
            "truncado": True,
            "tokens_orig": tokens_orig,
            "tokens_enviados": len(truncado) // self.CHARS_POR_TOKEN,
            "ratio": len(truncado) / len(texto),
        }
