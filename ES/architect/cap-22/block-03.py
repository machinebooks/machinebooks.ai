# Extraído de: LibroTecnico/cap-22-observabilidad.md
def log_audit_event(
    action: str,
    user_id: int = None,
    resource_type: str = None,
    resource_id: str = None,
    details: dict = None,
    severity: str = "INFO"
) -> None:
    """Registra un evento de auditoría y dispara alerta si es CRITICAL.

    El parámetro severity se puede calcular implícitamente según la acción,
    pero también se puede pasar explícitamente para overrides.
    """
    # Severity automática según tipo de acción
    critical_actions = {
        AuditActions.AI_CONFIG_CHANGED,
        AuditActions.BUDGET_LIMIT_CHANGED,
        AuditActions.CREDENTIAL_VAULT_ACCESS,
        AuditActions.PERMISSION_ESCALATION,
    }
    warning_actions = {
        AuditActions.LOGIN_FAILED,
        AuditActions.ACCESS_DENIED,
        AuditActions.MFA_DISABLED,
    }

    if action in critical_actions:
        severity = "CRITICAL"
    elif action in warning_actions and severity == "INFO":
        severity = "WARNING"

    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        details=details,
        ip_address=request.remote_addr if request else None,
        user_agent=request.user_agent.string if request else None,
        severity=severity,
        session_id=getattr(g, "session_id", None)
    )
    db.session.add(entry)
    db.session.commit()

    # Alerta automática para eventos críticos
    if severity == "CRITICAL":
        _trigger_security_alert(action, user_id, details)

def _trigger_security_alert(action: str, user_id: int, details: dict) -> None:
    """Envía notificación inmediata al equipo de seguridad para eventos críticos.
    Se ejecuta de forma asíncrona para no bloquear la petición del usuario."""
    from tasks.notifications import send_security_alert_task
    send_security_alert_task.delay(
        action=action,
        user_id=user_id,
        details=details,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
