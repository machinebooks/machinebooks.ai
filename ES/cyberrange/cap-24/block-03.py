# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Modelo de usuario con campos de seguridad
# Fichero: cyber-range-builder/backend/models.py

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(128), unique=True)
    hashed_pw = Column(String(255))
    role = Column(
        Enum('admin', 'red', 'blue', 'purple', 'organizer', 'viewer'),
        default='viewer'
    )
    workzone_id = Column(Integer, ForeignKey("workzone.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=True)

    # Campos de seguridad
    is_active = Column(Boolean, default=True)           # Desactivar sin eliminar
    failed_login_count = Column(Integer, default=0)      # Contador de intentos fallidos
    locked_until = Column(DateTime, nullable=True)       # Bloqueo temporal
    last_login = Column(DateTime, nullable=True)         # Último login exitoso
    must_change_password = Column(Boolean, default=False) # Forzar cambio en próximo login
    password_changed_at = Column(DateTime, nullable=True) # Control de rotación
    mfa_secret = Column(String(64), nullable=True)       # Secreto TOTP para MFA
    mfa_enabled = Column(Boolean, default=False)         # MFA activado
    session_token = Column(String(64), nullable=True)    # Para invalidar sesiones
