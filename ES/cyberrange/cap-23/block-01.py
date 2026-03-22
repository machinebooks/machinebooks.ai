# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: services/attack_runner.py
async def run_attack(db: Session, attack: AttackExecution, cmd: str):
    """Ejecutar un ataque y emitir cada línea al bus de eventos.
    NOTA DE SEGURIDAD: cmd proviene de ActionTemplate.default_cmd,
    definido exclusivamente por administradores — nunca contiene
    input directo de usuarios."""
    attack.state = "running"
    attack.started_at = datetime.utcnow()
    db.commit()

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    async def _stream():
        # Cada línea de stdout se publica en el topic del ataque
        async for line in proc.stdout:
            db.add(AttackLog(attack_id=attack.id, log_line=line.rstrip()))
            await event_bus.publish(f"attack.{attack.id}", line.rstrip())

    await asyncio.gather(_stream(), proc.wait())

    attack.state = "success" if proc.returncode == 0 else "failed"
    attack.finished_at = datetime.utcnow()
    db.commit()

    # Puntuación automática si el ataque fue exitoso
    if attack.state == "success":
        audit.add_score(
            db, user_id=attack.attacker_host_id,
            points=10, reason=f"Attack {attack.id} success"
        )
