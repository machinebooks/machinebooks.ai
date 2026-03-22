# Extraído de: LibroCyberrange/cap-12-sistema-ctf.md
@router.post("/challenges/{challenge_id}/unlock-hint")
def unlock_hint(
    challenge_id: int,
    hint_request: HintRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Desbloquea una pista sin descontar puntos inmediatamente.
    La penalización se aplica cuando el usuario capture la flag.
    """
    challenge = db.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(404, "Challenge no encontrado")

    hint = db.get(CtfHint, hint_request.hint_id)
    if not hint:
        raise HTTPException(404, "Pista no encontrada")

    # Verificar que el hint pertenece al challenge
    flag = db.get(CtfFlag, hint.flag_id)
    if not flag or flag.challenge_id != challenge_id:
        raise HTTPException(400, "La pista no pertenece a este challenge")

    # No permitir pistas en flags ya capturadas
    existing_capture = db.query(CtfCapture).filter(
        CtfCapture.flag_id == flag.id,
        CtfCapture.user_id == current_user.id
    ).first()
    if existing_capture:
        raise HTTPException(400, "Flag ya capturada, no puedes pedir pistas")

    # Si ya desbloqueó esta pista, devolver sin cobrar de nuevo
    existing_use = db.query(CtfHintUse).filter(
        CtfHintUse.hint_id == hint.id,
        CtfHintUse.user_id == current_user.id
    ).first()
    if existing_use:
        cost = max(1, (flag.points * hint.penalty_pct) // 100)
        return {
            "success": True,
            "hint_text": hint.text,
            "cost": cost,
            "already_unlocked": True
        }

    # Verificar instancia activa
    instance = db.query(ChallengeInstance).filter(
        ChallengeInstance.challenge_id == challenge_id,
        ChallengeInstance.user_id == current_user.id
    ).first()
    if not instance:
        raise HTTPException(400, "Debes iniciar el challenge primero")

    # Registrar uso de hint (sin capture_id por ahora)
    cost = max(1, (flag.points * hint.penalty_pct) // 100)
    db.add(CtfHintUse(
        hint_id=hint.id,
        user_id=current_user.id,
        instance_id=instance.id,
        capture_id=None  # Se vincula cuando capture la flag
    ))
    db.commit()

    return {
        "success": True,
        "hint_text": hint.text,
        "cost": cost,
        "already_unlocked": False
    }
