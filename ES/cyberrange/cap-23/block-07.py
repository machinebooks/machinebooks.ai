# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: WebSocketManager.send_to_session()
async def send_to_session(self, session_id: str,
                           message: Dict[str, Any]):
    """Enviar mensaje a una sesión, con buffer si la conexión se perdió"""
    message["timestamp"] = datetime.now().isoformat()
    found = False

    for websocket, metadata in list(self.connection_metadata.items()):
        if metadata["session_id"] == session_id:
            try:
                found = True
                await self.send_personal_message(websocket, message)
                break
            except Exception:
                self.disconnect(websocket)

    if not found and session_id in self.active_sessions:
        # La sesión existe pero la conexión se perdió:
        # almacenar mensajes críticos en buffer
        self.active_sessions[session_id]["status"] = "connection_lost"
        if message.get("type") in [
            "error", "execution_complete", "execution_failed"
        ]:
            buf = self.active_sessions[session_id].setdefault(
                "buffered_messages", []
            )
            buf.append(message)
