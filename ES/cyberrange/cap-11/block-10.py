# Extraído de: LibroCyberrange/cap-11-base-datos.md
class AuditLog(Base):
    """Registro de auditoría completo de la plataforma."""
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)

    # Clasificación del evento — tres dimensiones ortogonales
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_type = Column(Enum(
        'admin_action', 'user_action', 'gaming_event', 'security_event',
        'system_event', 'error', 'login_attempt', 'machine_operation',
        'playbook_execution', 'vm_lifecycle', 'api_call', 'database_operation'
    ), nullable=False, index=True)
    category = Column(Enum(
        'authentication', 'authorization', 'resource_management', 'security',
        'performance', 'configuration', 'gaming', 'infrastructure',
        'data_access', 'compliance', 'system_event'
    ), nullable=False, index=True)
    severity = Column(Enum('info', 'warning', 'error', 'critical', 'security'),
                      default='info', nullable=False, index=True)

    # Contexto del actor
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    session_id = Column(String(255), index=True)

    # Qué se hizo y sobre qué recurso
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), index=True)
    resource_id = Column(String(100), index=True)
    description = Column(Text, nullable=False)
    details = Column(JSON)

    # Resultado y contexto técnico
    status = Column(Enum('success', 'failure', 'pending', 'cancelled'),
                    default='success', nullable=False, index=True)
    module = Column(String(100), index=True)
    correlation_id = Column(String(100), index=True)  # Agrupa eventos relacionados
    duration_ms = Column(Integer)

    # Revisión de seguridad
    review_status = Column(Enum('unreviewed', 'reviewing', 'reviewed',
                                 'flagged', 'resolved'),
                           default='unreviewed', nullable=False, index=True)
    reviewed_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    review_notes = Column(Text)
