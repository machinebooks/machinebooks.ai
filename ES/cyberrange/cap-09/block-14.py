# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# Tres canales WebSocket en main.py
@app.websocket("/ws/playbook/{session_id}")
async def websocket_playbook_execution(websocket: WebSocket, session_id: str):
    """Streaming de ejecución de playbooks Ansible."""
    ...

@app.websocket("/ws/powershell/{session_id}")
async def websocket_powershell_execution(websocket: WebSocket, session_id: str):
    """Streaming de ejecución de scripts PowerShell."""
    ...

@app.websocket("/ws/logs")
async def websocket_system_logs(websocket: WebSocket):
    """Logs del sistema en tiempo real."""
    ...
