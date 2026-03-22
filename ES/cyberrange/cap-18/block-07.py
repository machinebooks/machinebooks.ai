# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/coaching_websocket.py
import socketio
from backend.services.ai.coaching_service import CoachingService
from backend.services.ai.action_tracker import ActionTracker
from backend.database import SessionLocal

# Socket.IO server (compartido con el resto del Cyber Range)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

coaching_service = CoachingService()
action_tracker = ActionTracker()

# Tarea periódica que evalúa estancamiento para sesiones activas
async def proactive_coaching_loop():
    """
    Ejecuta cada 60 segundos. Para cada sesión activa, evalúa
    si el jugador está atascado y envía pista proactiva si procede.
    """
    while True:
        db = SessionLocal()
        try:
            active_sessions = action_tracker.get_active_sessions()

            for session_key in active_sessions:
                user_id, challenge_id = session_key.split(":")

                # Verificar que el jugador tiene coaching proactivo activado
                if not _is_proactive_enabled(int(user_id)):
                    continue

                hint = await coaching_service.generate_proactive_hint(
                    db=db,
                    user_id=int(user_id),
                    challenge_id=int(challenge_id)
                )

                if hint:
                    # Enviar pista por WebSocket al jugador específico
                    await sio.emit(
                        "coaching_hint",
                        {
                            "hint": hint["hint"],
                            "level": hint["level"],
                            "penalty_pct": hint["penalty_pct"],
                            "mode": "proactive",
                            "stall_reason": hint.get("stall_reason", ""),
                        },
                        room=f"user_{user_id}"
                    )
        finally:
            db.close()

        await asyncio.sleep(60)  # Evaluar cada minuto


@sio.on("terminal_command")
async def handle_terminal_command(sid, data):
    """
    Recibe cada comando que el jugador ejecuta en la consola VNC.
    Lo registra en el tracker de acciones para análisis de coaching.
    """
    user_id = data.get("user_id")
    challenge_id = data.get("challenge_id")
    command = data.get("command", "")

    if not user_id or not challenge_id or not command:
        return

    action_tracker.track_command(
        user_id=int(user_id),
        challenge_id=int(challenge_id),
        command=command,
        output_summary=data.get("output_summary")
    )


@sio.on("toggle_proactive_coaching")
async def toggle_proactive(sid, data):
    """
    Permite al jugador activar/desactivar el coaching proactivo.
    El botón 'estoy trabajando, no me interrumpas'.
    """
    user_id = data.get("user_id")
    enabled = data.get("enabled", True)
    _set_proactive_enabled(int(user_id), enabled)
    await sio.emit(
        "coaching_status",
        {"proactive_enabled": enabled},
        room=f"user_{user_id}"
    )
