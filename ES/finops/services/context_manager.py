# Extraído de: LibroFinOps/cap-09-cache-prompt-batch.md
# services/context_manager.py
from dataclasses import dataclass

@dataclass
class RAGFragment:
    """Fragmento recuperado del índice vectorial (Qdrant)."""
    text:        str
    score:       float   # relevancia semántica, de 0 a 1
    source:      str     # documento de origen
    token_count: int     # tokens estimados del fragmento

class ContextManager:
    """
    Gestiona el contexto RAG para maximizar relevancia por token.
    Aplica truncación cuando el contexto supera el presupuesto.
    """

    DEFAULT_CONTEXT_BUDGET = 1_500  # tokens máximos para contexto RAG

    def build_context(
        self,
        fragments: list[RAGFragment],
        budget_tokens: int = DEFAULT_CONTEXT_BUDGET,
    ) -> tuple[str, dict]:
        """
        Construye el contexto RAG dentro del presupuesto de tokens.
        Prioriza fragmentos de mayor relevancia semántica (mayor score).

        Devuelve: (texto del contexto, estadísticas de truncación).
        """
        # Ordenar por relevancia descendente
        sorted_frags = sorted(fragments, key=lambda f: f.score, reverse=True)

        selected = []
        tokens_used = 0

        for frag in sorted_frags:
            if tokens_used + frag.token_count <= budget_tokens:
                selected.append(frag)
                tokens_used += frag.token_count
            # Si no cabe, saltarlo y probar el siguiente (puede ser más corto)

        tokens_total = sum(f.token_count for f in fragments)
        tokens_dropped = tokens_total - tokens_used

        context_parts = [
            f"[Fuente: {f.source}]\n{f.text}" for f in selected
        ]

        stats = {
            "fragments_total":   len(fragments),
            "fragments_used":    len(selected),
            "tokens_used":       tokens_used,
            "tokens_dropped":    tokens_dropped,
            # Ratio de truncación: 0.0 = sin truncación, 1.0 = todo descartado
            "truncation_ratio":  tokens_dropped / max(1, tokens_total),
        }

        return "\n\n---\n\n".join(context_parts), stats
