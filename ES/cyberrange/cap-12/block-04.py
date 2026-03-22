# Extraído de: LibroCyberrange/cap-12-sistema-ctf.md
import hmac
import html
import time as _time
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    Challenge, ChallengeInstance, CtfFlag,
    CtfCapture, CtfHint, CtfHintUse, ScoreLog
)
from backend.auth import get_current_user

router = APIRouter(prefix="/gaming", tags=["Gaming Zone"])

# --- Rate limiter en memoria ---
_flag_attempts: dict[int, list[float]] = defaultdict(list)
FLAG_RATE_LIMIT = 10   # máximo intentos
FLAG_RATE_WINDOW = 60   # por ventana de 60 segundos


def _check_rate_limit(user_id: int) -> bool:
    """True si el usuario excede el límite de intentos."""
    now = _time.time()
    attempts = _flag_attempts[user_id]
    # Purgar intentos fuera de la ventana
    _flag_attempts[user_id] = [
        t for t in attempts if now - t < FLAG_RATE_WINDOW
    ]
    if len(_flag_attempts[user_id]) >= FLAG_RATE_LIMIT:
        return True
    _flag_attempts[user_id].append(now)
    return False


@router.post("/submit-flag")
def submit_flag(
    submission: FlagSubmission,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Envío de flag con scoring completo y protecciones."""

    # 1. Rate limiting: 10 intentos/minuto
    if _check_rate_limit(current_user.id):
        raise HTTPException(429, "Demasiados intentos. Espera un minuto.")

    # 2. Sanitización contra XSS/injection
    sanitized_flag = html.escape(submission.flag_token.strip())

    # 3. Verificar instancia activa
    instance = db.query(ChallengeInstance).filter(
        ChallengeInstance.challenge_id == submission.challenge_id,
        ChallengeInstance.user_id == current_user.id,
        ChallengeInstance.state == 'open'
    ).first()

    if not instance:
        raise HTTPException(400, "Debes iniciar el challenge primero")

    # 4. Verificar tiempo límite
    challenge = db.get(Challenge, submission.challenge_id)
    if challenge and challenge.time_limit_minutes and instance.started_at:
        elapsed = (datetime.utcnow() - instance.started_at).total_seconds() / 60
        if elapsed > challenge.time_limit_minutes:
            instance.state = 'done'
            db.commit()
            raise HTTPException(403, "Tiempo límite agotado")

    # 5. Buscar flag con comparación timing-safe
    flags = db.query(CtfFlag).filter(
        CtfFlag.challenge_id == submission.challenge_id
    ).all()

    flag = None
    for f in flags:
        # hmac.compare_digest evita timing attacks
        if hmac.compare_digest(f.flag_token, sanitized_flag):
            flag = f
            break

    if not flag:
        return {"success": False, "message": "Flag incorrecta"}

    # 6. Verificar duplicado
    if db.query(CtfCapture).filter_by(
        instance_id=instance.id, flag_id=flag.id
    ).first():
        return {"success": False, "message": "Ya has capturado esta flag"}

    # 7. Registrar captura
    now = datetime.utcnow()
    capture = CtfCapture(
        instance_id=instance.id,
        flag_id=flag.id,
        user_id=current_user.id,
        captured_at=now
    )
    db.add(capture)

    # 8. Calcular scoring con penalización de hints
    flag_points = flag.points
    hints_penalty = 0

    hints_used = db.query(CtfHintUse).join(CtfHint).filter(
        CtfHintUse.user_id == current_user.id,
        CtfHint.flag_id == flag.id
    ).all()

    for hint_use in hints_used:
        hint = db.get(CtfHint, hint_use.hint_id)
        if hint:
            penalty = max(1, (flag.points * hint.penalty_pct) // 100)
            hints_penalty += penalty
            # Vincular pista con captura (vinculación diferida)
            hint_use.capture_id = capture.id

    final_points = max(0, flag_points - hints_penalty)

    # 9. First blood bonus: +25% si es la primera captura global
    first_blood_bonus = 0
    previous_captures = db.query(CtfCapture).filter(
        CtfCapture.flag_id == flag.id,
        CtfCapture.id != capture.id
    ).count()

    if previous_captures == 0:
        first_blood_bonus = max(1, flag_points // 4)  # 25%
        final_points += first_blood_bonus

    # 10. Actualizar score de la instancia
    instance.score += final_points

    # 11. Registrar en score_log para auditoría
    reason = f"Flag capturada (base: {flag.points}"
    if hints_penalty > 0:
        reason += f", hints: -{hints_penalty}"
    if first_blood_bonus > 0:
        reason += f", first blood: +{first_blood_bonus}"
    reason += ")"

    db.add(ScoreLog(
        user_id=current_user.id,
        points=final_points,
        reason=reason,
        ts=now
    ))

    # 12. Verificar completación del challenge
    total_flags = db.query(CtfFlag).filter(
        CtfFlag.challenge_id == submission.challenge_id
    ).count()
    captured_flags = db.query(CtfCapture).filter(
        CtfCapture.instance_id == instance.id
    ).count()

    challenge_completed = captured_flags >= total_flags
    if challenge_completed:
        instance.state = 'done'
        instance.completed_at = now
        # Bonus por completar: 50 pts base + bonus configurado
        bonus = (challenge.bonus_points or 0) + 50
        instance.score += bonus
        db.add(ScoreLog(
            user_id=current_user.id,
            points=bonus,
            reason=f"Challenge completado: {challenge.title}",
            ts=now
        ))

    db.commit()

    return {
        "success": True,
        "points": final_points,
        "base_points": flag.points,
        "hints_penalty": hints_penalty,
        "first_blood_bonus": first_blood_bonus,
        "completed": challenge_completed,
        "total_score": instance.score
    }
