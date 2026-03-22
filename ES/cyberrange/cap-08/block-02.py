# Extraído de: LibroCyberrange/cap-08-workzones.md
# Ejemplo didáctico: services/workzone_gc.py — Garbage collector

async def gc_loop():
    """Tarea asíncrona cada 15 min: destruir workzones caducadas."""
    while True:
        try:
            now = datetime.datetime.utcnow()
            with SessionLocal() as db:
                workzones = db.query(Workzone).all()

                for wz in workzones:
                    ttl = wz.zone_ttl_hours or 24  # 24h por defecto

                    if wz.created_at and \
                       (now - wz.created_at).total_seconds() > ttl * 3600:

                        logger.info(
                            f"Workzone {wz.id} ({wz.name}) expirada, "
                            f"iniciando limpieza..."
                        )

                        # 1. Apagar y eliminar escenarios desplegados
                        scenarios = db.query(Scenario).filter_by(
                            workzone_id=wz.id
                        ).all()
                        for sc in scenarios:
                            try:
                                scenario_ops.power_off_all(db, sc.id)
                                db.delete(sc)
                            except Exception as e:
                                logger.error(
                                    f"Error eliminando escenario {sc.id}: {e}"
                                )

                        # 2. Desvincular usuarios
                        users = db.query(User).filter_by(
                            workzone_id=wz.id
                        ).all()
                        for user in users:
                            user.workzone_id = None
                            logger.info(
                                f"Usuario {user.email} removido "
                                f"de la workzone {wz.id}"
                            )

                        # 3. Eliminar workzone
                        db.delete(wz)
                        logger.info(f"Workzone {wz.id} eliminada")

                db.commit()

        except Exception as e:
            logger.error(f"Error en garbage collector: {e}")

        await asyncio.sleep(900)  # 15 minutos
