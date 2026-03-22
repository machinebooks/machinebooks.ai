# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: Health check periódico
async def ping_connections(self):
    """Verificar que las conexiones están vivas enviando ping"""
    disconnected = set()

    for conn_type, websockets in self.active_connections.items():
        for websocket in list(websockets):
            try:
                await websocket.ping()
            except Exception:
                disconnected.add(websocket)

    # Limpiar conexiones muertas
    for websocket in disconnected:
        self.disconnect(websocket)

    return len(disconnected)

def cleanup_old_sessions(self, max_age_hours: int = 24):
    """Eliminar sesiones inactivas de más de 24 horas"""
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    old = [
        sid for sid, session in self.active_sessions.items()
        if session["started_at"] < cutoff
        and session.get("status") != "running"
    ]
    for sid in old:
        del self.active_sessions[sid]
    return len(old)
