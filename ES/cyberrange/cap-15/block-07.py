# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
@router.websocket("/ws/{attack_id}")
async def ws_attack(websocket: WebSocket, attack_id: int):
    await websocket.accept()
    try:
        async for line in event_bus.subscribe(f"attack.{attack_id}"):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        pass
