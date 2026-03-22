# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: services/websocket_manager.py (estructura)
class WebSocketManager:
    """Gestor centralizado de conexiones WebSocket"""

    def __init__(self):
        # Conexiones activas agrupadas por tipo
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "playbook_execution": set(),
            "powershell_execution": set(),
            "system_logs": set()
        }

        # Metadatos de cada conexión (tipo, sesión, timestamp)
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

        # Sesiones de ejecución activas con su estado y buffer
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
