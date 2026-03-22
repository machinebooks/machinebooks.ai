# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/backend/main.py (startup tasks)

@app.on_event("startup")
async def startup():
    # 1. Garbage collector de workzones (asyncio task)
    # Comprueba TTL cada 15 min, destruye las expiradas
    asyncio.create_task(workzone_gc.gc_loop())

    # 2. Sincronización automática Proxmox → MySQL (APScheduler)
    # Reconcilia el estado cada 15 min
    auto_sync_service.start()

    # 3. Limpieza de instancias de challenges (APScheduler)
    # Destruye VMs huérfanas de retos terminados
    challenge_cleanup_service.start()
