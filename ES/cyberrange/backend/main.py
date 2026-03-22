# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/main.py — Ciclo de vida de la aplicación
from backend.services import workzone_gc
from backend.services.challenge_cleanup_service import challenge_cleanup_service

@app.on_event("startup")
async def _startup():
    # 1. Garbage collector de workzones vencidas
    asyncio.create_task(workzone_gc.gc_loop())

    # 2. Limpieza de instancias de challenges (LXC/QEMU huérfanas)
    try:
        challenge_cleanup_service.start()
    except Exception as e:
        logger.error(f"Error iniciando challenge cleanup service: {e}")

@app.on_event("shutdown")
async def _shutdown():
    try:
        challenge_cleanup_service.stop()
    except Exception as e:
        logger.error(f"Error deteniendo challenge cleanup service: {e}")
