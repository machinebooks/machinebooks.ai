# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/backend/workzone_gc.py

async def gc_loop():
    """Tarea asíncrona: destruye workzones caducadas cada 15 minutos."""
    while True:
        try:
            now = datetime.utcnow()
            with SessionLocal() as db:
                workzones = db.query(Workzone).all()

                for wz in workzones:
                    ttl_hours = 24    # Por defecto, 24 horas de vida

                    if wz.created_at and (now - wz.created_at).total_seconds() > ttl_hours * 3600:
                        logger.info(f"Workzone {wz.id} ({wz.name}) expirada, limpiando...")

                        # 1. Apagar y eliminar escenarios asociados
                        scenarios = db.query(Scenario).filter_by(workzone_id=wz.id).all()
                        for sc in scenarios:
                            try:
                                scenario_ops.power_off_all(db, sc.id)
                                db.delete(sc)
                            except Exception as e:
                                logger.error(f"Error eliminando escenario {sc.id}: {e}")

                        # 2. Liberar usuarios asignados a esta workzone
                        users = db.query(User).filter_by(workzone_id=wz.id).all()
                        for user in users:
                            user.workzone_id = None

                        # 3. Eliminar la workzone
                        db.delete(wz)
                        logger.info(f"Workzone {wz.id} eliminada")

                db.commit()

        except Exception as e:
            logger.error(f"Error en garbage collector: {e}")

        await asyncio.sleep(900)   # 15 minutos entre ciclos
