# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: routers/ws_deploy.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services import event_bus
from backend.auth import verify_token

router = APIRouter(prefix="/ws")

@router.websocket("/deploy/{deploy_id}")
async def ws_deploy(websocket: WebSocket, deploy_id: str):
    """Streaming de despliegue: bus de eventos → WebSocket.
    Requiere JWT válido como primer mensaje tras la conexión."""
    await websocket.accept()

    # Autenticación obligatoria: el primer mensaje debe ser el JWT
    try:
        auth_message = await asyncio.wait_for(
            websocket.receive_text(), timeout=10.0
        )
        payload = verify_token(auth_message)
    except (asyncio.TimeoutError, JWTError, Exception):
        await websocket.close(code=4001, reason="Token inválido o ausente")
        return

    try:
        async for line in event_bus.subscribe(f"deploy.{deploy_id}"):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        pass  # El generador se limpia automáticamente
