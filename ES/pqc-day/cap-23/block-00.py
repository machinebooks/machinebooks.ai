# Extraído de: LibroPQC/cap-23-observabilidad.md
from extensions import db
from datetime import datetime


class AuditLog(db.Model):
    """Registro de auditoría para acciones de usuario.
    Cada fila responde: quién hizo qué, cuándo, desde dónde
    y sobre qué entidad del sistema."""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    # Quién: relación con tabla de usuarios
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True  # Permite acciones del sistema sin usuario
    )
    # Qué: acción ejecutada (login, create_client, run_scan, etc.)
    action = db.Column(db.String(100), nullable=False)
    # Sobre qué: tipo de entidad y su ID
    entity_type = db.Column(db.String(50))  # 'client', 'scan', 'report'
    entity_id = db.Column(db.Integer)
    # Contexto adicional: JSON libre para metadatos específicos
    details = db.Column(db.JSON)
    # Desde dónde: IP y navegador del usuario
    ip_address = db.Column(db.String(45))   # IPv6 soportado
    user_agent = db.Column(db.Text)
    # Cuándo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación para resolver el nombre del usuario en consultas
    user = db.relationship(
        'User',
        backref=db.backref('audit_logs', lazy='dynamic'),
        foreign_keys=[user_id]
    )
