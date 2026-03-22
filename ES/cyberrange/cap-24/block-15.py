# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Revisión de eventos de auditoría
# Fichero: cyber-range-builder/backend/routers/admin_audit.py

@router.put("/logs/{log_id}/review", response_model=AuditLogResponse)
def review_audit_log(
    log_id: int,
    review_data: AuditLogReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marcar un log como revisado — la revisión queda registrada.
    Quién revisó, cuándo y qué notas dejó forman parte de la traza."""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")

    # Actualizar estado de revisión
    log.review_status = review_data.review_status  # reviewing/reviewed/flagged/resolved
    log.review_notes = review_data.review_notes
    log.reviewed_by = current_user.id
    log.reviewed_at = datetime.utcnow()

    db.commit()

    # Registrar la propia revisión como evento de auditoría
    AuditService.log_event(
        db=db,
        event_type='admin_action',
        category='compliance',
        action='review_audit_log',
        description=f"Usuario {current_user.email} revisó log {log_id} "
                    f"como {review_data.review_status}",
        user_id=current_user.id,
        username=current_user.email,
        resource_type='audit_log',
        resource_id=str(log_id),
        module='audit',
        function='review_audit_log'
    )
