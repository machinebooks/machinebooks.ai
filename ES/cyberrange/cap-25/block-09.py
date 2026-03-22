# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/backend/startup_lifecycle.py

@app.on_event("startup")
async def _startup():
    # 1. Garbage collector de workzones (cada 15 min)
    asyncio.create_task(workzone_gc.gc_loop())

    # 2. Sincronización automática Proxmox (cada 2 min)
    try:
        auto_sync_service.start()
    except Exception as e:
        logger.error(f"Error iniciando sincronización automática: {e}")

    # 3. Limpieza de instancias de challenges (cada 10 min)
    try:
        challenge_cleanup_service.start()
    except Exception as e:
        logger.error(f"Error iniciando challenge cleanup: {e}")

@app.on_event("shutdown")
async def _shutdown():
    auto_sync_service.stop()
    challenge_cleanup_service.stop()
