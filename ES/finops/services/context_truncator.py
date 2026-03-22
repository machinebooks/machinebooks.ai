# Extraído de: LibroFinOps/cap-25-caso-tokens.md
# services/context_truncator.py
# Truncado inteligente: envía al modelo solo lo que necesita.
# Reducción media del 30% en tokens de entrada.

class ContextTruncator:
    """
    Estrategia por operación:
    - Clasificación: 500 tokens (cabecera)
    - Extracción: 8.000 tokens (entidades al inicio)
    - Resumen: inicio + fin (sandwich)
    - Recomendación: cabecera + cláusulas relevantes
    """
    MAX_TOKENS = {
        "clasificacion": 500,
        "extraccion_entidades": 8_000,
        "resumen_ejecutivo": 12_000,
        "recomendacion_accion": 10_000,
    }
    CHARS_POR_TOKEN = 4  # Aproximación para español

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
