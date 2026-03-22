# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/routers/ws_deploy.py — Canal de despliegue
@router.websocket("/deploy/{deploy_id}")
async def ws_deploy(websocket: WebSocket, deploy_id: str):
    await websocket.accept()
    try:
        async for line in event_bus.subscribe(f"deploy.{deploy_id}"):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        pass
