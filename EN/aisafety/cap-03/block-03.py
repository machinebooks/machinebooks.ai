# Extracted from: LibroAISafety/ch-03-inside-the-model.md
# Security token budget for a context window
# Example for a system with agents and RAG

CONTEXT_WINDOW = 200_000  # available tokens

# Security budget: minimum 5% of total context
SECURITY_BUDGET = int(CONTEXT_WINDOW * 0.05)  # 10,000 tokens

SECURITY_DISTRIBUTION = {
    "main_system_prompt": 3_000,           # base instructions
    "system_prompt_sandwich": 1_500,       # repetition at end
    "rag_prefixes": 500,                   # before each document
    "tool_suffixes": 500,                  # after each tool result
    "periodic_reminders": 2_000,           # every 20K tokens of history
    "validation_reserve": 2_500,           # for dynamic filters
}

# Tokens available for user content
CONTENT_TOKENS = CONTEXT_WINDOW - SECURITY_BUDGET
# 190,000 tokens for actual content

def verify_budget(security_tokens_used: int) -> bool:
    """Verifies that the security budget is maintained.
    If it drops below 3%, emit alert."""
    ratio = security_tokens_used / CONTEXT_WINDOW
    if ratio < 0.03:
        # Alert: security instructions are
        # underrepresented in the context
        return False
    return True
