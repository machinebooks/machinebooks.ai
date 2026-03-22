# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: services/websocket_manager.py
async def stream_to_websocket(session_id: str, line: str,
                               stream_type: str = "playbook",
                               max_retries: int = 3, **kwargs):
    """Función de utilidad para streaming con backoff exponencial"""
    for attempt in range(max_retries):
        try:
            if stream_type == "playbook":
                await websocket_manager.stream_playbook_output(
                    session_id, line, kwargs.get("execution_id")
                )
            elif stream_type == "powershell":
                await websocket_manager.stream_powershell_output(
                    session_id, line, kwargs.get("script_name")
                )
            return  # Éxito

        except Exception as e:
            if attempt < max_retries - 1:
                wait = 0.5 * (attempt + 1)  # Backoff: 0.5s, 1s, 1.5s
                await asyncio.sleep(wait)
            else:
                logger.error(
                    f"Error definitivo streaming a {session_id} "
                    f"tras {max_retries} intentos: {e}"
                )
                # No propagar: la ejecución del playbook
                # no debe fallar por un error de WebSocket
