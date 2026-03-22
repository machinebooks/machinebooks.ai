# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Modelo de auditoría — campos principales
# Fichero: cyber-range-builder/backend/models.py

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)

    # Información temporal (indexada para búsquedas por rango)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Tipo de evento: 12 tipos que cubren todo el ciclo de vida
    event_type = Column(Enum(
        'admin_action',        # Acciones administrativas
        'user_action',         # Acciones de usuarios
        'gaming_event',        # Eventos del motor de juego
        'security_event',      # Eventos de seguridad
        'system_event',        # Eventos del sistema
        'error',               # Errores de la plataforma
        'login_attempt',       # Intentos de login (éxito y fallo)
        'machine_operation',   # Operaciones con máquinas virtuales
        'playbook_execution',  # Ejecución de playbooks Ansible
        'vm_lifecycle',        # Ciclo de vida de VMs
        'api_call',            # Llamadas a API
        'database_operation',  # Operaciones de BD
        name='audit_event_type'
    ), nullable=False, index=True)

    # Categorización cruzada para análisis multidimensional
    category = Column(Enum(
        'authentication',      # Autenticación y autorización
        'authorization',       # Permisos y roles
        'resource_management', # Gestión de recursos
        'security',            # Eventos de seguridad
        'performance',         # Rendimiento del sistema
        'configuration',       # Cambios de configuración
        'gaming',              # Actividades de gaming/CTF
        'infrastructure',      # Infraestructura (VMs, redes)
        'data_access',         # Acceso a datos sensibles
        'compliance',          # Cumplimiento y auditoría
        'system_event',        # Eventos del sistema
        name='audit_category'
    ), nullable=False, index=True)

    # Severidad — 5 niveles
    severity = Column(Enum(
        'info', 'warning', 'error', 'critical', 'security',
        name='audit_severity'
    ), default='info', nullable=False, index=True)

    # Contexto del usuario y la petición
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, index=True)
    username = Column(String(100), index=True)
    ip_address = Column(String(45), index=True)  # Soporta IPv6
    user_agent = Column(Text)
    session_id = Column(String(255), index=True)

    # Qué se hizo y sobre qué recurso
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), index=True)
    resource_id = Column(String(100), index=True)
    resource_name = Column(String(255))
    description = Column(Text, nullable=False)
    details = Column(JSON)  # Detalles técnicos en formato libre

    # Resultado
    status = Column(Enum('success', 'failure', 'pending', 'cancelled',
                         name='audit_status'), default='success')
    error_code = Column(String(50))
    error_message = Column(Text)

    # Contexto técnico para correlación
    module = Column(String(100), index=True)
    function = Column(String(100))
    request_id = Column(String(100), index=True)
    correlation_id = Column(String(100), index=True)  # Agrupar eventos relacionados

    # Métricas de rendimiento
    duration_ms = Column(Integer)
    response_size = Column(Integer)
    query_count = Column(Integer)

    # Metadatos para investigación forense
    tags = Column(JSON)
    flags = Column(JSON)  # { "requires_review": true, ... }
    review_status = Column(Enum(
        'unreviewed', 'reviewing', 'reviewed', 'flagged', 'resolved',
        name='review_status'
    ), default='unreviewed', nullable=False, index=True)
    reviewed_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
