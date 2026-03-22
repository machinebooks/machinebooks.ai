# Extraído de: LibroCISO/cap-22-observabilidad-siem.md
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.models.base import Base


class AccessLog(Base):
    """Registro de acceso para auditoría ENS (op.exp.8).

    Tabla de solo inserción: no se permiten UPDATE ni DELETE.
    La retención se gestiona con tarea Celery periódica.
    """
    __tablename__ = "access_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    user_id = Column(String(64), nullable=False, index=True)
    corporate_id = Column(String(64), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv6 max length
    action = Column(String(50), nullable=False, index=True)
    # Acciones: login, logout, login_failed, mfa_challenge,
    #   mfa_success, mfa_failed, role_change, module_access,
    #   data_export, config_change, ai_request, ai_override
    result = Column(String(20), nullable=False)  # success, failure
    failure_reason = Column(String(255), nullable=True)
    module = Column(String(50), nullable=True)
    resource_id = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    session_id = Column(String(64), nullable=True)
    request_id = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)  # JSON con contexto adicional

    # Sin métodos de update ni delete en el modelo
    # La integridad se protege a nivel de permisos de BD:
    # GRANT INSERT, SELECT ON access_log TO 'grc_app'@'%';
    # (sin UPDATE ni DELETE)
