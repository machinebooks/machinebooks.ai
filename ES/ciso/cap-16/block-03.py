# Extraído de: LibroCISO/cap-16-rbac-multitenancy.md
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean
from app.models.base import db


class Role(db.Model):
    """Definición de rol con permisos granulares por módulo.

    Los permisos se almacenan como JSON con estructura:
    {
        "privacy": ["read", "write", "admin"],
        "risk": ["read"],
        "compliance": ["read", "write"],
        "ai": ["execute"],
        "audit": ["read"]
    }
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corporate_id = Column(
        Integer, ForeignKey("corporates.id"),
        nullable=True,  # NULL = rol global del sistema
        comment="NULL para roles de sistema, valor para roles custom del tenant"
    )
    name = Column(String(100), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    permissions = Column(
        JSON, nullable=False,
        comment="Mapa módulo → [acciones permitidas]"
    )
    is_system = Column(
        Boolean, default=False,
        comment="True = rol predefinido, no editable por el tenant"
    )
    is_active = Column(Boolean, default=True)

    # Permisos específicos para módulos de IA
    ai_permissions = Column(
        JSON, nullable=True,
        default=None,
        comment="Agentes y herramientas IA permitidos para este rol"
    )
