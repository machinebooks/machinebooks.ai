# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
def _check_intermediate_text(self, response_content: list) -> Optional[GuardrailResult]:
    """
    Verifica guardrails de salida en bloques de texto intermedios del bucle.
    Se invoca antes de ejecutar las herramientas de cada iteración.
    """
    for block in response_content:
        if block.type == "text" and block.text.strip():
            # Guardrail de credenciales sobre texto intermedio
            if self._contains_credentials(block.text):
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    reason="Credenciales detectadas en razonamiento intermedio del agente"
                )
            # Guardrail de exposición de system prompt
            if self._contains_system_prompt_leak(block.text):
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    reason="Posible exposición de system prompt en respuesta intermedia"
                )
    return None  # Sin hallazgos
