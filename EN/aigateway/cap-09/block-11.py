# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/compression/message_stubbing.py:73-93 (synthesized)
def truncate_message(message: dict, max_tokens: int) -> dict:
    target_chars = max(100, max_tokens * 3)
    lines = content.split("\n")
    first_count = (target_lines * 7) // 10    # 70% first lines
    last_count = max(1, target_lines - first_count)  # 30% last lines
    truncated = "\n".join(lines[:first_count]) + "\n...[truncado]..." + "\n".join(lines[-last_count:])
    return {**message, "content": truncated}
