# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/services/websocket_manager.py
# Gestor centralizado de conexiones WebSocket

from fastapi import WebSocket
from typing import Dict, Set, Any
from datetime import datetime
import uuid

class WebSocketManager:
    """
    Gestiona todas las conexiones WebSocket del Cyber Range.

    Tres tipos de conexión:
    - playbook_execution: streaming de logs de Ansible
    - powershell_execution: streaming de scripts remotos
    - system_logs: logs generales del sistema
    """

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "playbook_execution": set(),
            "powershell_execution": set(),
            "system_logs": set(),
        }
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket,
                      connection_type: str,
                      session_id: str = None) -> str:
        """Acepta una conexión y la registra por tipo."""
        await websocket.accept()
        session_id = session_id or str(uuid.uuid4())

        self.active_connections[connection_type].add(websocket)
        self.connection_metadata[websocket] = {
            "type": connection_type,
            "session_id": session_id,
            "connected_at": datetime.now(),
        }

        # Si es una reconexión, enviar mensajes pendientes
        if session_id in self.active_sessions:
            await self.recover_session_messages(session_id, websocket)

        return session_id

    async def broadcast(self, connection_type: str, message: dict):
        """Envía un mensaje a todos los clientes de un tipo."""
        dead = set()
        for ws in self.active_connections[connection_type]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        # Limpiar conexiones muertas
        for ws in dead:
            self.disconnect(ws)
