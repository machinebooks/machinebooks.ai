# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/models/audit.py — Modelo de auditoría
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer,
        db.ForeignKey('organizations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                        ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))    # 'client', 'analysis', 'user'
    entity_id = db.Column(db.Integer)
    details = db.Column(db.JSON)               # Contexto adicional
    ip_address = db.Column(db.String(45))      # IPv4 o IPv6
    user_agent = db.Column(db.Text)            # Navegador/cliente
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con usuario (SET NULL si se borra el usuario)
    user = db.relationship('User', backref=db.backref(
        'audit_logs', lazy='dynamic'
    ))

    @staticmethod
    def log(organization_id, user_id, action, entity_type=None,
            entity_id=None, details=None, ip_address=None,
            user_agent=None):
        """Registra una acción en el registro de auditoría."""
        entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(entry)
        db.session.commit()
        return entry
