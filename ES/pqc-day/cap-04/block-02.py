# Extraído de: LibroPQC/cap-04-requisito-arquitectura.md
# Ejemplo didáctico: patrones/models/organization.py
from app import db
from datetime import datetime

class Organization(db.Model):
    """Organización: unidad raíz de aislamiento multi-tenant.

    Cada organización tiene su propio conjunto de usuarios,
    clientes, proyectos, hallazgos y configuraciones.
    Los planes de suscripción controlan los límites de uso.
    """
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    subscription_plan = db.Column(
        db.Enum('free', 'starter', 'professional', 'enterprise'),
        default='free',
        nullable=False
    )

    # Límites del plan — configurables sin redespliegue
    max_clients = db.Column(db.Integer, default=1)
    max_users = db.Column(db.Integer, default=1)
    max_analyses_per_month = db.Column(db.Integer, default=5)
    analyses_this_month = db.Column(db.Integer, default=0)
    analyses_month_reset = db.Column(db.Date)

    # Feature flags por plan — JSON flexible
    features = db.Column(db.JSON, default=dict)
    # Ejemplo: {"cloud_analysis": true, "ai_semantic": true,
    #           "agent_autonomous": false, "pdf_reports": true,
    #           "api_access": false, "sso": false}

    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relaciones — cascade para integridad referencial
    users = db.relationship(
        'User', backref='organization',
        cascade='all, delete-orphan', lazy='dynamic'
    )
    clients = db.relationship(
        'Client', backref='organization',
        cascade='all, delete-orphan', lazy='dynamic'
    )
    audit_logs = db.relationship(
        'AuditLog', backref='organization',
        cascade='all, delete-orphan', lazy='dynamic'
    )

    def can_add_client(self) -> bool:
        """Verifica si la organización puede añadir un cliente."""
        if self.subscription_plan == 'enterprise':
            return True
        return self.clients.count() < self.max_clients

    def can_add_user(self) -> bool:
        """Verifica si la organización puede registrar un usuario."""
        if self.subscription_plan == 'enterprise':
            return True
        return self.users.count() < self.max_users

    def can_run_analysis(self) -> bool:
        """Verifica si quedan análisis disponibles este mes."""
        if self.subscription_plan == 'enterprise':
            return True
        self._reset_monthly_counter()
        return self.analyses_this_month < self.max_analyses_per_month

    def _reset_monthly_counter(self):
        """Reinicia el contador si el mes ha cambiado."""
        today = datetime.utcnow().date()
        if self.analyses_month_reset is None or \
           self.analyses_month_reset.month != today.month:
            self.analyses_this_month = 0
            self.analyses_month_reset = today
            db.session.commit()
