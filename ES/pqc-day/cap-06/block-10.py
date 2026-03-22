# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/models/user.py — Modelo con RBAC integrado
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer,
        db.ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    role = db.Column(db.Enum(
        'org_owner', 'org_admin', 'analyst', 'viewer', 'client_user'
    ), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    # Constraints de unicidad compuestos
    __table_args__ = (
        db.UniqueConstraint('organization_id', 'email',
                           name='unique_org_email'),
        db.UniqueConstraint('organization_id', 'username',
                           name='unique_org_username'),
    )

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'organization_id': self.organization_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat()
                          if self.last_login else None
        }
        # password_hash NUNCA se incluye por defecto
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data
