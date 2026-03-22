# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: main.py — Endpoint WebSocket de playbook
@app.websocket("/ws/playbook/{session_id}")
async def websocket_playbook_execution(
    websocket: WebSocket, session_id: str
):
    """WebSocket para streaming de ejecución de playbooks.
    Requiere JWT válido como primer mensaje tras la conexión."""
    await websocket.accept()

    # Autenticación obligatoria: primer mensaje = JWT
    try:
        auth_msg = await asyncio.wait_for(
            websocket.receive_text(), timeout=10.0
        )
        payload = verify_token(auth_msg)
    except (asyncio.TimeoutError, JWTError, Exception):
        await websocket.close(code=4001, reason="Token inválido o ausente")
        return

    try:
        actual_session_id = await websocket_manager.connect(
            websocket, "playbook_execution", session_id
        )

        # Enviar estado inicial si hay sesión activa
        session_status = websocket_manager.get_session_status(session_id)
        if session_status:
            await websocket_manager.send_personal_message(websocket, {
                "type": "session_status",
                "session_id": session_id,
                "status": session_status.get("status", "unknown"),
                "execution_id": session_status.get("execution_id"),
                "message": f"Reconectado a sesión {session_id}"
            })

        # Bucle de escucha: mantener la conexión viva
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data.get("type") == "ping":
                await websocket_manager.send_personal_message(
                    websocket,
                    {"type": "pong",
                     "timestamp": datetime.now().isoformat()}
                )
            elif data.get("type") == "status_request":
                status = websocket_manager.get_session_status(session_id)
                await websocket_manager.send_personal_message(
                    websocket,
                    {"type": "status_response",
                     "session_id": session_id,
                     "status": status}
                )

    except WebSocketDisconnect:
        pass  # Desconexión limpia del cliente
    finally:
        websocket_manager.disconnect(websocket)
        websocket_manager.cleanup_dead_connections()
