# Extraído de: LibroCyberrange/cap-11-base-datos.md
class SecurityAlert(Base):
    """Alerta de seguridad generada por análisis de logs de auditoría."""
    __tablename__ = "security_alerts"
    id = Column(Integer, primary_key=True)
    alert_type = Column(Enum(
        'failed_login_attempts', 'suspicious_activity', 'privilege_escalation',
        'unusual_access_pattern', 'data_exfiltration', 'system_compromise',
        'malware_detection', 'unauthorized_access', 'configuration_change',
        'resource_abuse'
    ), nullable=False, index=True)
    severity = Column(Enum('low', 'medium', 'high', 'critical'), nullable=False)
    priority = Column(Enum('p1', 'p2', 'p3', 'p4'), nullable=False)

    # Contexto
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    detection_rule = Column(String(100))      # Qué regla disparó la alerta
    evidence = Column(JSON)                   # Evidencia del evento
    related_log_ids = Column(JSON)            # IDs de audit_logs relacionados
    false_positive_score = Column(SmallInteger, default=0)  # 0-100

    # Ciclo de vida de la alerta
    status = Column(Enum('open', 'investigating', 'confirmed',
                          'false_positive', 'resolved', 'suppressed'))
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    occurrence_count = Column(Integer, default=1)
