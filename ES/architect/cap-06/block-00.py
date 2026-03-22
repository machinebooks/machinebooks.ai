# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
class UserAppMembership(db.Model):
    """Asignación de usuario a aplicación con rol específico.
    Un usuario puede estar en varias apps con roles distintos."""
    __tablename__ = 'user_app_memberships'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('app_roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    granted_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'app_id', name='uq_user_app'),
    )
