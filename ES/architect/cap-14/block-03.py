# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
UNIVERSAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Lee el contenido de un fichero. Soporta .docx (texto por secciones "
                "con headings), .xlsx/.xlsm (estructura de hojas y celdas), .pdf "
                "(texto extraído), .txt/.json/.csv (contenido raw). "
                "Para .docx también devuelve índice de tablas."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta del fichero"},
                    "section": {
                        "type": "string",
                        "description": "Opcional: heading de sección específica (.docx)"
                    }
                },
                "required": ["path"]
            }
        }
    },
    # edit_file, write_file, run_command, search, done (6 en total)
]
