# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: WebSocketManager.connect()
async def connect(self, websocket: WebSocket,
                  connection_type: str,
                  session_id: str = None) -> str:
    """Conectar un cliente, detectando reconexiones automáticamente"""
    await websocket.accept()

    if connection_type not in self.active_connections:
        connection_type = "system_logs"  # Fallback seguro

    self.active_connections[connection_type].add(websocket)

    if not session_id:
        session_id = str(uuid.uuid4())

    # Detectar reconexión: misma sesión, conexión nueva
    session_exists = session_id in self.active_sessions
    is_reconnection = session_exists

    self.connection_metadata[websocket] = {
        "type": connection_type,
        "session_id": session_id,
        "connected_at": datetime.now(),
        "is_reconnection": is_reconnection
    }

    if is_reconnection:
        # Enviar mensajes acumulados durante la desconexión
        await self.recover_session_messages(session_id, websocket)
    else:
        await self.send_personal_message(websocket, {
            "type": "connection_established",
            "session_id": session_id,
            "connection_type": connection_type,
            "timestamp": datetime.now().isoformat()
        })

    return session_id
