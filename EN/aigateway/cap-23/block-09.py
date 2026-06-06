# Extracted from: LibroAIGateway/cap-23-compliance-regulatory.md
# gateway/app/tasks/retention_purge.py:166-167
def _safe_identifier(name: str) -> bool:
    return bool(name) and all(c.isalnum() or c == "_" for c in name)
