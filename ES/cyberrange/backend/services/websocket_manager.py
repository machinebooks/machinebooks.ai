# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/services/websocket_manager.py — Gestor centralizado
class WebSocketManager:
    """Gestor de WebSockets para streaming en tiempo real."""

    def __init__(self):
        # Conexiones activas por tipo de canal
        self.active_connections: dict[str, set[WebSocket]] = {
            "playbook_execution": set(),
            "powershell_execution": set(),
            "system_logs": set()
        }
        # Metadatos por conexión
        self.connection_metadata: dict[WebSocket, dict] = {}
        # Estado de sesiones de ejecución activas
        self.active_sessions: dict[str, dict] = {}

    async def connect(self, websocket: WebSocket,
                      connection_type: str, session_id: str = None):
        """Conectar un cliente, detectar reconexiones."""
        await websocket.accept()

        if connection_type not in self.active_connections:
            connection_type = "system_logs"

        self.active_connections[connection_type].add(websocket)

        if not session_id:
            session_id = str(uuid.uuid4())

        # Detectar reconexión: la sesión ya existe
        is_reconnection = session_id in self.active_sessions
        if is_reconnection:
            await self.recover_session_messages(session_id, websocket)
        else:
            await self.send_personal_message(websocket, {
                "type": "connection_established",
                "session_id": session_id,
                "connection_type": connection_type,
                "timestamp": datetime.now().isoformat()
            })

        return session_id

    def disconnect(self, websocket: WebSocket):
        """Limpiar conexión y metadatos."""
        for conn_set in self.active_connections.values():
            conn_set.discard(websocket)
        self.connection_metadata.pop(websocket, None)
