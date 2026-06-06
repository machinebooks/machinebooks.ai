# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# gateway/app/api/v1/realtime.py (sintético)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/api/v1/realtime/events")
async def realtime_events(websocket: WebSocket):
    # 1. AUTH antes de aceptar: token por query o subprotocolo
    token = websocket.query_params.get("token") or _token_from_subprotocol(websocket)
    claims = await authenticate_ws(token, origin=websocket.headers.get("origin"))
    if claims is None or not _role_allowed(claims):
        await websocket.close(code=4401)   # fail-closed: sin auth, no hay stream
        return
    await websocket.accept()

    channel = RedisChannel("gateway_events")
    try:
        while True:
            # 2. Revalidar revocacion a mitad de sesion
            if await is_revoked(claims["jti"]):
                await websocket.close(code=4401)
                return
            message = await channel.consume(timeout=30)
            if message:
                await websocket.send_json({"type": "event", "data": message})
            else:
                # 3. Ping cada 30s para mantener viva la conexion
                await websocket.send_json({"type": "ping", "ts": datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        await channel.close()
