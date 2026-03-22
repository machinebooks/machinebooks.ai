# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
class AuditLog(db.Model):
    """Log de auditoría enterprise con acciones predefinidas y severidad."""
    __tablename__ = 'audit_logs'
    __bind_key__ = 'platform_core'

    # Acciones predefinidas — autenticación
    LOGIN_SUCCESS         = 'LOGIN_SUCCESS'
    LOGIN_FAILED          = 'LOGIN_FAILED'
    TOKEN_REFRESH         = 'TOKEN_REFRESH'
    SESSION_INVALIDATED   = 'SESSION_INVALIDATED'
    MFA_ENABLED           = 'MFA_ENABLED'
    MFA_BYPASS_ATTEMPTED  = 'MFA_BYPASS_ATTEMPTED'
    OAUTH2_CONNECTED      = 'OAUTH2_CONNECTED'
    # Acciones predefinidas — autorización
    ACCESS_DENIED         = 'ACCESS_DENIED'
    PERMISSION_CHANGED    = 'PERMISSION_CHANGED'
    ROLE_ASSIGNED         = 'ROLE_ASSIGNED'
    # Acciones predefinidas — datos sensibles
    SENSITIVE_DATA_ACCESS    = 'SENSITIVE_DATA_ACCESS'
    CREDENTIAL_VAULT_ACCESS  = 'CREDENTIAL_VAULT_ACCESS'
    CREDENTIAL_ROTATED       = 'CREDENTIAL_ROTATED'
    # Acciones predefinidas — IA y configuración
    LLM_INVOCATION        = 'LLM_INVOCATION'
    GUARDRAIL_TRIGGERED   = 'GUARDRAIL_TRIGGERED'
    MODEL_CONFIG_CHANGED  = 'MODEL_CONFIG_CHANGED'
    # Acciones predefinidas — gestión de usuarios
    USER_CREATED          = 'USER_CREATED'
    USER_DEACTIVATED      = 'USER_DEACTIVATED'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, nullable=True)
    action      = db.Column(db.String(50), nullable=False)
    severity    = db.Column(db.String(20), default='INFO')  # INFO/WARNING/CRITICAL
    details     = db.Column(db.Text, nullable=True)
    ip_address  = db.Column(db.String(45), nullable=True)   # IPv4 + IPv6
    user_agent  = db.Column(db.String(500), nullable=True)
    request_id  = db.Column(db.String(36), nullable=True)   # Correlación con logs HTTP
    created_at  = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        db.Index('idx_audit_user_action', 'user_id', 'action'),
        db.Index('idx_audit_severity_date', 'severity', 'created_at'),
    )
