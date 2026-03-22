# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: WebSocketManager.recover_session_messages()
async def recover_session_messages(self, session_id: str,
                                    websocket: WebSocket):
    """Enviar mensajes acumulados en buffer a un cliente reconectado"""
    if session_id not in self.active_sessions:
        return

    session = self.active_sessions[session_id]
    buffered = session.get("buffered_messages", [])

    if buffered:
        # Notificar al cliente que hay mensajes pendientes
        await self.send_personal_message(websocket, {
            "type": "session_recovered",
            "session_id": session_id,
            "buffered_count": len(buffered),
            "status": session.get("status", "unknown")
        })

        # Enviar cada mensaje acumulado
        for message in buffered:
            await self.send_personal_message(websocket, message)

        # Limpiar buffer tras envío exitoso
        session["buffered_messages"] = []
        session["status"] = "reconnected"
