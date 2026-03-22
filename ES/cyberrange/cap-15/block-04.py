# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
LOG_DIR = os.getenv("ACTION_LOG_DIR", "/var/log/cyber-range/actions")
os.makedirs(LOG_DIR, exist_ok=True)

async def run_attack(db: Session, attack: AttackExecution, cmd: str):
    # NOTA DE SEGURIDAD: cmd proviene de ActionTemplate.default_cmd,
    # definido exclusivamente por administradores. Nunca contiene input
    # directo de usuarios. create_subprocess_shell es necesario aquí
    # porque los comandos usan pipes y redirecciones del shell.
    attack.state = "running"
    attack.started_at = datetime.datetime.utcnow()
    db.commit()

    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    async def _stream():
        async for raw in proc.stdout:
            line = raw.decode(errors="replace")
            # Persistir cada línea para el rastro forense
            db.add(AttackLog(
                attack_id=attack.id,
                log_line=line.rstrip()
            ))
            # Publicar en el bus de eventos para WebSocket
            await event_bus.publish(
                f"attack.{attack.id}", line.rstrip()
            )

    await asyncio.gather(_stream(), proc.wait())

    attack.state = "success" if proc.returncode == 0 else "failed"
    attack.finished_at = datetime.datetime.utcnow()
    db.commit()

    # Puntuación: +10 por ataque exitoso
    if attack.state == "success":
        audit.add_score(
            db, user_id=attack.attacker_host_id,
            points=10, reason=f"Attack {attack.id} success"
        )
