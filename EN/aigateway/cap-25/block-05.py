# Extracted from: LibroAIGateway/cap-25-mcp-registration-catalog.md
def _validate_mcp_stdio_command(command: str) -> None:
    for token in (";", "&&", "||", "|", ">", "<", "`", "$("):
        if token in raw:
            raise HTTPException(400, f"character not allowed: {token!r}")
    if ".." in raw:
        raise HTTPException(400, "path traversal blocked")
    binary = raw.split()[0]
    for prefix in ("/bin/", "/sbin/", "/usr/sbin/"):
        if binary.startswith(prefix):
            raise HTTPException(400, f"binary in {prefix} not allowed")
    resolved = os.path.realpath(binary)
    if resolved not in whitelist and binary not in whitelist:
        raise HTTPException(400, f"binary not in whitelist")
