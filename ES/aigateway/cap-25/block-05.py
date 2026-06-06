# Extraído de: LibroAIGateway/cap-25-mcp-registro-catalogo.md
def _validate_mcp_stdio_command(command: str) -> None:
    for token in (";", "&&", "||", "|", ">", "<", "`", "$("):
        if token in raw:
            raise HTTPException(400, f"caracter no permitido: {token!r}")
    if ".." in raw:
        raise HTTPException(400, "path traversal bloqueado")
    binary = raw.split()[0]
    for prefix in ("/bin/", "/sbin/", "/usr/sbin/"):
        if binary.startswith(prefix):
            raise HTTPException(400, f"binario en {prefix} no permitido")
    resolved = os.path.realpath(binary)
    if resolved not in whitelist and binary not in whitelist:
        raise HTTPException(400, f"binario no en whitelist")
