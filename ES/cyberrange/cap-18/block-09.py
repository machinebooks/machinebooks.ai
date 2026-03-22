# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: integración con el sistema de scoring existente
def _record_hint_use(
    self, db: Session, user_id: int, challenge_id: int,
    hint_text: str, level: int, penalty_pct: int
):
    """
    Registra el uso de una pista de coaching IA en el sistema
    de hints existente, manteniendo compatibilidad con el scoring.
    """
    # Obtener o crear la instancia del challenge
    instance = db.query(ChallengeInstance).filter_by(
        user_id=user_id,
        challenge_id=challenge_id,
        state="open"
    ).first()

    if not instance:
        logger.warning(f"No se encontró instancia activa: user={user_id}, challenge={challenge_id}")
        return

    # Crear un CtfHint dinámico para la pista IA
    # (los hints estáticos son predefinidos; los de IA se crean en tiempo real)
    ai_hint = CtfHint(
        flag_id=None,  # Las pistas IA no están vinculadas a una flag específica
        text=hint_text,
        penalty_pct=penalty_pct,
        order_idx=level,  # El nivel de escalación como orden
    )
    db.add(ai_hint)
    db.flush()  # Para obtener el ID

    # Registrar el uso
    hint_use = CtfHintUse(
        hint_id=ai_hint.id,
        user_id=user_id,
        instance_id=instance.id,
        used_at=datetime.utcnow()
    )
    db.add(hint_use)
    db.commit()

    logger.info(
        f"Coaching hint registrado: user={user_id}, challenge={challenge_id}, "
        f"level={level}, penalty={penalty_pct}%"
    )
