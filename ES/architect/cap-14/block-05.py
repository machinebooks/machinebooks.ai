# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
TOOL_HANDLERS = {
    "read_file":  lambda **kw: read_file(kw.get("path", ""), kw.get("section", "")),
    "edit_file":  lambda **kw: edit_file(
        kw.get("path", ""), kw.get("old_text", ""), kw.get("new_text", ""),
        kw.get("replace_all", True), kw.get("cell", "")
    ),
    "write_file": lambda **kw: write_file(
        kw.get("path", ""), kw.get("content", ""), kw.get("sheets")
    ),
    "run_command": lambda **kw: run_command(
        kw.get("command", ""), kw.get("timeout", 30)
    ),
    # search y done se gestionan desde el propio agente (requieren estado async)
}
