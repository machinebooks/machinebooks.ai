# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
# Servicio de auditoría y puntuación
def log_event(db: Session, session_id: int, etype: str, details: dict):
    ev = AuditEvent(
        session_id=session_id,
        event_type=etype,
        details=details,
        ts=datetime.datetime.utcnow(),
    )
    db.add(ev); db.commit()

def add_score(db: Session, user_id: int, points: int, reason: str):
    db.add(ScoreLog(
        user_id=user_id,
        points=points,
        reason=reason,
        ts=datetime.datetime.utcnow(),
    ))
    db.commit()
