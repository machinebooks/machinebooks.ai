# Extraído de: LibroBugBounty/cap-26-caso-discord.md
def analyze_electron_fuses(exe_path):
    """Extraer y decodificar Electron fuses."""
    with open(exe_path, "rb") as f:
        data = f.read()

    # Sentinel de Electron fuses
    sentinel = b"dL7pKGdnNz796PbbjQWNKmHXBZaB9tsX"
    idx = data.find(sentinel)
    if idx == -1:
        return None

    fuse_start = idx + len(sentinel)
    version = data[fuse_start]
    count = data[fuse_start + 1]
    fuse_bytes = data[fuse_start + 2:fuse_start + 2 + count]

    NAMES = [
        "RUN_AS_NODE", "COOKIE_ENCRYPTION",
        "NODE_OPTIONS", "NODE_CLI_INSPECT",
        "EMBEDDED_ASAR_INTEGRITY_VALIDATION",
        "ONLY_LOAD_APP_FROM_ASAR",
        "LOAD_BROWSER_PROCESS_V8_SNAPSHOT",
        "GRANT_FILE_PROTOCOL_EXTRA_PRIVILEGES",
    ]

    results = {}
    for i, b in enumerate(fuse_bytes):
        name = NAMES[i] if i < len(NAMES) else f"UNKNOWN_{i}"
        state = {0x30: "DISABLED", 0x31: "ENABLED",
                 0x00: "REMOVED"}.get(b, "UNKNOWN")
        results[name] = state
    return results
