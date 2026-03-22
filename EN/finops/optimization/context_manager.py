# Source: The FinOps Engineer and the Machine -- Chapter 9
# Pattern: Context window manager for token optimization

# services/context_manager.py
from dataclasses import dataclass

@dataclass
class RAGFragment:
    """Fragment retrieved from the vector index (Qdrant)."""
    text:        str
    score:       float   # semantic relevance, from 0 to 1
    source:      str     # source document
    token_count: int     # estimated tokens in the fragment

class ContextManager:
    """
    Manages RAG context to maximize relevance per token.
    Applies truncation when the context exceeds the budget.
    """

    DEFAULT_CONTEXT_BUDGET = 1_500  # maximum tokens for RAG context

    def build_context(
        self,
        fragments: list[RAGFragment],
        budget_tokens: int = DEFAULT_CONTEXT_BUDGET,
    ) -> tuple[str, dict]:
        """
        Builds the RAG context within the token budget.
        Prioritizes fragments with the highest semantic relevance (highest score).

        Returns: (context text, truncation statistics).
        """
        # Sort by descending relevance
        sorted_frags = sorted(fragments, key=lambda f: f.score, reverse=True)

        selected = []
        tokens_used = 0

        for frag in sorted_frags:
            if tokens_used + frag.token_count <= budget_tokens:
                selected.append(frag)
                tokens_used += frag.token_count
            # If it doesn't fit, skip it and try the next (it may be shorter)

        tokens_total = sum(f.token_count for f in fragments)
        tokens_dropped = tokens_total - tokens_used

        context_parts = [
            f"[Source: {f.source}]\n{f.text}" for f in selected
        ]

        stats = {
            "fragments_total":   len(fragments),
            "fragments_used":    len(selected),
            "tokens_used":       tokens_used,
            "tokens_dropped":    tokens_dropped,
            # Truncation ratio: 0.0 = no truncation, 1.0 = everything discarded
            "truncation_ratio":  tokens_dropped / max(1, tokens_total),
        }

        return "\n\n---\n\n".join(context_parts), stats
