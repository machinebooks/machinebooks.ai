# Extraído de: LibroCyberrange/cap-03-arquitecto-cyber-range.md
# Rate limiting en flag submission para prevenir timing attacks
# Ejemplo didáctico: patrones/ctf/flag_submit.py

import hmac
import hashlib
import time
from datetime import datetime, timezone

# Límite: máximo 10 envíos por minuto por equipo
FLAG_SUBMIT_RATE_LIMIT = "10/minute"

@router.post("/api/v1/flags/{flag_id}/submit")
@require_permission("flag.submit")
@rate_limit(FLAG_SUBMIT_RATE_LIMIT, key_func=get_team_id)
async def submit_flag(flag_id: int, submission: FlagSubmission):
    """Verifica un flag enviado por un participante.

    Usa comparación constant-time para prevenir timing attacks:
    el tiempo de respuesta es idéntico para flags correctos e
    incorrectos, evitando que un atacante deduzca el flag
    carácter a carácter midiendo tiempos de respuesta.
    """
    flag = await get_flag_or_404(flag_id)
    team = g.current_user.team

    # Verificar que el flag pertenece al ejercicio del equipo
    if flag.exercise_id != team.exercise_id:
        audit_log(
            action="FLAG_SUBMIT_WRONG_EXERCISE",
            severity="WARNING",
            user_id=g.current_user.id,
            detail=f"Intento de submit en ejercicio ajeno"
        )
        raise HTTPException(status_code=403)

    # Comparación constant-time — CRÍTICO para seguridad
    # hmac.compare_digest previene timing attacks
    submitted_hash = hashlib.sha256(
        submission.value.encode()
    ).hexdigest()
    is_correct = hmac.compare_digest(submitted_hash, flag.hash_value)

    # Registrar intento independientemente del resultado
    audit_log(
        action="FLAG_SUBMITTED",
        severity="INFO",
        user_id=g.current_user.id,
        workzone_id=team.workzone_id,
        exercise_id=flag.exercise_id,
        metadata={
            "flag_id": flag_id,
            "correct": is_correct,
            "attempt_number": await get_attempt_count(team.id, flag_id) + 1
        }
    )

    if is_correct:
        await award_points(team, flag)
        return {"status": "correct", "points": flag.points}

    return {"status": "incorrect"}
