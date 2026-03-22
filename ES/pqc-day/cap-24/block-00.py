# Extraído de: LibroPQC/cap-24-saas.md
from app.extensions import db
from datetime import datetime


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    # Plan y límites — el corazón del modelo SaaS
    subscription_plan = db.Column(
        db.Enum('free', 'starter', 'professional', 'enterprise'),
        default='free'
    )
    max_clients = db.Column(db.Integer, default=1)       # Free: 1
    max_users = db.Column(db.Integer, default=1)          # Free: 1
    max_analyses_per_month = db.Column(db.Integer, default=5)  # Free: 5

    # Feature flags como JSON — flexibilidad sin migraciones
    features = db.Column(db.JSON)
    # Ejemplo: {"cloud_analysis": false, "ai_semantic": false,
    #           "compliance_reports": false, "autonomous_agent": false,
    #           "api_access": false, "sso": false}

    is_active = db.Column(db.Boolean, default=True)
    billing_email = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # Relaciones — la organización es el nodo raíz del grafo de datos
    users = db.relationship('User', backref='organization',
                           lazy='dynamic', cascade='all, delete-orphan')
    clients = db.relationship('Client', backref='organization',
                             lazy='dynamic', cascade='all, delete-orphan')
