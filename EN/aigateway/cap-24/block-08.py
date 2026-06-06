# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# gateway/app/api/v1/realtime.py (synthetic)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/api/v1/realtime/events")
async def realtime_events(websocket: WebSocket):
    # 1. AUTH before accept: token via query or subprotocol
    token = websocket.query_params.get("token") or _token_from_subprotocol(websocket)
    claims = await authenticate_ws(token, origin=websocket.headers.get("origin"))
    if claims is None or not _role_allowed(claims):
        await websocket.close(code=4401)   # fail-closed: no auth, no stream
        return
    await websocket.accept()

    channel = RedisChannel("gateway_events")
    try:
        while True:
            # 2. Re-validate revocation mid-session
            if await is_revoked(claims["jti"]):
                await websocket.close(code=4401)
                return
            message = await channel.consume(timeout=30)
            if message:
                await websocket.send_json({"type": "event", "data": message})
            else:
                # 3. Ping every 30s to keep the connection alive
                await websocket.send_json({"type": "ping", "ts": datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        await channel.close()
