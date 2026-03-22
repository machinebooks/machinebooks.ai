# Extraído de: LibroCISO/cap-09-nis2-dora-tsunami.md
# Modelo de licencia de módulo — gate técnico y comercial
# Cada tenant puede tener múltiples módulos con distintas fechas

from sqlalchemy import (
    Column, String, DateTime, JSON,
    Enum as SQLEnum, BigInteger, ForeignKey
)
from app.models.base import BaseModel  # multi-tenant, audit, soft delete


class LicenseStatus(str, PyEnum):
    """Estados posibles de una licencia."""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class LicenseModule(BaseModel):
    """Licencia de módulo sectorial por tenant.

    Hereda de BaseModel: corporate_id, created_at, updated_at,
    created_by, is_deleted (soft delete).
    """
    __tablename__ = "license_modules"

    # Identificación
    module_name = Column(
        String(50), nullable=False, index=True,
        comment="Nombre del módulo: nis2, dora, dsa, bcm..."
    )
    display_name = Column(
        String(200), nullable=False,
        comment="Nombre legible: 'NIS2 - Directiva 2022/2555'"
    )

    # Temporalidad
    starts_at = Column(
        DateTime(timezone=True), nullable=False,
        comment="Inicio de la licencia"
    )
    expires_at = Column(
        DateTime(timezone=True), nullable=True,
        comment="Expiración. NULL = sin caducidad"
    )

    # Estado
    status = Column(
        SQLEnum(LicenseStatus), nullable=False,
        default=LicenseStatus.ACTIVE,
        comment="Estado actual de la licencia"
    )

    # Feature flags — granularidad dentro del módulo
    feature_flags = Column(
        JSON, nullable=True, default=dict,
        comment="Flags de funcionalidad: {'tlpt_enabled': true, ...}"
    )

    # Metadatos
    max_users = Column(
        BigInteger, nullable=True,
        comment="Límite de usuarios para este módulo. NULL = sin límite"
    )
    notes = Column(
        String(1000), nullable=True,
        comment="Notas administrativas sobre la licencia"
    )
