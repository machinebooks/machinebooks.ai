# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/backend/main.py (WebSocket endpoints)

@app.websocket("/ws/playbook/{session_id}")
async def websocket_playbook_execution(
    websocket: WebSocket,
    session_id: str
):
    """
    Streaming en tiempo real de ejecución de playbooks Ansible.
    El frontend abre esta conexión cuando el operador lanza un playbook,
    y recibe cada línea de output conforme Ansible la genera.
    """
    try:
        actual_id = await websocket_manager.connect(
            websocket, "playbook_execution", session_id
        )

        while True:
            # Escuchar mensajes del cliente (ping, status_request)
            message = await websocket.receive_text()
            data = json.loads(message)

            if data.get("type") == "ping":
                await websocket_manager.send_personal_message(
                    websocket,
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket)
