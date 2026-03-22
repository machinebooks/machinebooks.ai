# Extraído de: LibroPQC/cap-04-requisito-arquitectura.md
# Ejemplo didáctico: patrones/models/user.py
from app import db
from passlib.hash import bcrypt

class User(db.Model):
    """Usuario con RBAC vinculado a una organización.

    El organization_id es el ancla de aislamiento: todo lo que
    el usuario puede ver y hacer está filtrado por su organización.
    El role determina qué acciones puede ejecutar dentro de ella.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    role = db.Column(
        db.Enum('org_owner', 'org_admin', 'analyst', 'viewer', 'client_user'),
        nullable=False,
        default='analyst'
    )
    organization_id = db.Column(
        db.Integer,
        db.ForeignKey('organizations.id'),
        nullable=False
    )
    # Para client_user: a qué cliente pertenece
    client_id = db.Column(
        db.Integer,
        db.ForeignKey('clients.id'),
        nullable=True  # Solo aplica si role == 'client_user'
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def set_password(self, password: str):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)

    def has_permission(self, permission: str) -> bool:
        """Verifica si el rol del usuario incluye un permiso."""
        return permission in ROLE_PERMISSIONS.get(self.role, set())

# Mapa de permisos por rol — explícito, sin magia
ROLE_PERMISSIONS = {
    'org_owner': {
        'manage_subscription', 'manage_users', 'manage_clients',
        'run_analysis', 'view_findings', 'generate_reports',
        'manage_integrations', 'manage_ai', 'view_audit',
        'delete_organization'
    },
    'org_admin': {
        'manage_users', 'manage_clients', 'run_analysis',
        'view_findings', 'generate_reports', 'manage_integrations',
        'manage_ai', 'view_audit'
    },
    'analyst': {
        'manage_clients', 'run_analysis', 'view_findings',
        'generate_reports', 'use_chat_ai'
    },
    'viewer': {
        'view_findings', 'view_audit'
    },
    'client_user': {
        'view_own_findings'  # Solo datos de su propio cliente
    }
}
