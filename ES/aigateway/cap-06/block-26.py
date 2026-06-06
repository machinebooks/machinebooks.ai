# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
_SECRET_RE = re.compile(
    r"(sk-[a-zA-Z0-9_\-]{16,}|Bearer\s+[A-Za-z0-9_\-\.]{10,}|[A-Fa-f0-9]{32,})"
)
