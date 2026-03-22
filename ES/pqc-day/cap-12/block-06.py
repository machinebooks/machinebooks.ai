# Extraído de: LibroPQC/cap-12-agente-autonomo.md
def _call_with_prompt_tools(self, base_url, messages, model, timeout):
    """
    Fallback: inyectar herramientas como texto en el prompt.
    Para modelos que no soportan tool-calling nativo.
    """
    # Generar descripción textual de las herramientas
    tool_prompt = """
## HERRAMIENTAS DISPONIBLES
Para usar una herramienta, escribe un bloque JSON así:
