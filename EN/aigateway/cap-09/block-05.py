# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/compression/smart_compression.py:45-62
def _get_protected_indices(messages: list[dict]) -> set[int]:
    protected: set[int] = set()
    last_user = None
    last_assistant = None
    for i, msg in enumerate(messages):
        role = msg.get("role")
        if role == "system":
            protected.add(i)
        elif role == "user":
            last_user = i
        elif role == "assistant":
            last_assistant = i
    if last_user is not None:
        protected.add(last_user)
    if last_assistant is not None:
        protected.add(last_assistant)
    return protected
