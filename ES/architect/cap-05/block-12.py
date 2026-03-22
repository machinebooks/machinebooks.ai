# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
class AppRole(db.Model):
    """Rol de usuario dentro de una aplicación específica.
    Un mismo usuario puede tener roles distintos en cada app."""
    __tablename__ = 'app_roles'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    # Ejemplos: "analyst", "manager", "viewer", "admin"

    # Permisos granulares por módulo (JSON para flexibilidad)
    permissions = db.Column(db.JSON, nullable=False, default=dict)
    # Ejemplo: {"clients": ["read", "write"], "proposals": ["read"]}

    # Control de acceso a módulos IA
    ai_modules_access = db.Column(db.JSON, default=list)
    # Ejemplo: ["document_analyzer", "proposal_generator"]

    # Bypass para roles de administración
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('app_id', 'name', name='uq_approle_app_name'),
    )
