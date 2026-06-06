# Extracted from: LibroAIGateway/cap-07-adapters.md
_SENSITIVE_RE = re.compile(
    r"(sk-[a-zA-Z0-9\-_]{16,}|Bearer\s+[A-Za-z0-9\-_.]{10,}"
    r"|api[_\-]?key[\"'\s:=]+[A-Za-z0-9\-_.]{10,}"
    r"|[A-Za-z0-9]{32,})",                 # 4th alternative: long tokens with no prefix
    re.IGNORECASE,
)
def _sanitize_error(msg: str) -> str:
    return _SENSITIVE_RE.sub("[REDACTED]", msg[:200])
