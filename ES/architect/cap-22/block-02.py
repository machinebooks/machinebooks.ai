# Extraído de: LibroTecnico/cap-22-observabilidad.md
from datetime import datetime, timezone
from sqlalchemy import Index
from extensions import db

class AuditLog(db.Model):
    """Registro de auditoría de acciones de negocio y seguridad.

    Separado de los logs técnicos — sirve para compliance, auditorías
    de seguridad y respuesta ante incidentes, no para depuración.
    """
    __tablename__ = 'audit_logs'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)

    # Quién — puede ser null si la acción ocurre antes de autenticar
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)

    # Qué
    action = db.Column(db.String(100), nullable=False)  # Constante predefinida
    resource_type = db.Column(db.String(50), nullable=True)  # 'document', 'proposal', 'user'
    resource_id = db.Column(db.String(100), nullable=True)

    # Contexto
    details = db.Column(db.JSON, nullable=True)  # Metadatos adicionales de la acción
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 e IPv6
    user_agent = db.Column(db.String(500), nullable=True)

    # Clasificación
    severity = db.Column(db.String(20), default='INFO')  # INFO, WARNING, CRITICAL

    # Cuándo
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Índices compuestos para las consultas más frecuentes en el panel de auditoría
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_timestamp_severity', 'created_at', 'severity'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )


class AuditActions:
    """Constantes predefinidas de acciones auditables.

    Usar siempre estas constantes en lugar de strings libres —
    esto garantiza consistencia y facilita las queries de análisis.
    """
    # Autenticación
    LOGIN_SUCCESS          = "LOGIN_SUCCESS"
    LOGIN_FAILED           = "LOGIN_FAILED"
    LOGOUT                 = "LOGOUT"
    MFA_ENABLED            = "MFA_ENABLED"
    MFA_DISABLED           = "MFA_DISABLED"
    MFA_VERIFIED           = "MFA_VERIFIED"
    PASSWORD_CHANGED       = "PASSWORD_CHANGED"
    TOKEN_REFRESHED        = "TOKEN_REFRESHED"

    # Control de acceso
    ACCESS_DENIED          = "ACCESS_DENIED"
    PERMISSION_ESCALATION  = "PERMISSION_ESCALATION"

    # Datos sensibles
    SENSITIVE_DATA_ACCESS  = "SENSITIVE_DATA_ACCESS"
    DOCUMENT_DOWNLOADED    = "DOCUMENT_DOWNLOADED"
    BULK_EXPORT            = "BULK_EXPORT"

    # Configuración de IA (operaciones críticas)
    AI_CONFIG_CHANGED      = "AI_CONFIG_CHANGED"
    PROMPT_MODIFIED        = "PROMPT_MODIFIED"
    MODEL_SWITCHED         = "MODEL_SWITCHED"
    BUDGET_LIMIT_CHANGED   = "BUDGET_LIMIT_CHANGED"

    # Administración
    USER_CREATED           = "USER_CREATED"
    USER_DEACTIVATED       = "USER_DEACTIVATED"
    ROLE_ASSIGNED          = "ROLE_ASSIGNED"
    CREDENTIAL_VAULT_ACCESS = "CREDENTIAL_VAULT_ACCESS"
