# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
import enum
from sqlalchemy import Boolean, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.mysql import DATETIME, JSON
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel


class PolicyCategory(str, enum.Enum):
    """Categorías de políticas de seguridad."""
    INFORMATION_SECURITY = "information_security"
    ACCESS_CONTROL = "access_control"
    INCIDENT_MANAGEMENT = "incident_management"
    BCM = "bcm"                     # Continuidad de negocio
    CRYPTOGRAPHY = "cryptography"
    PHYSICAL_SECURITY = "physical_security"
    SUPPLY_CHAIN = "supply_chain"
    ACCEPTABLE_USE = "acceptable_use"
    DATA_CLASSIFICATION = "data_classification"
    REMOTE_WORK = "remote_work"
    BYOD = "byod"                   # Dispositivos personales
    OTHER = "other"


class PolicyStatus(str, enum.Enum):
    """Ciclo de vida de una política de seguridad."""
    DRAFT = "draft"           # Borrador inicial
    REVIEW = "review"         # En revisión por responsables
    APPROVED = "approved"     # Aprobada por dirección
    PUBLISHED = "published"   # Publicada y accesible
    ARCHIVED = "archived"     # Retirada o sustituida
    NEEDS_UPDATE = "needs_update"  # Necesita revisión


class SecurityPolicy(BaseModel):
    """Política de seguridad con versionado y ciclo de vida.

    Cada política tiene propietario, versión, marcos aplicables
    y opción de requerir confirmación de lectura.
    """
    __tablename__ = "pa_security_policies"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    policy_code: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True,
        comment="Código interno: POL-SEC-001"
    )
    category: Mapped[str] = mapped_column(
        Enum(PolicyCategory), nullable=False,
        default=PolicyCategory.INFORMATION_SECURITY
    )
    status: Mapped[str] = mapped_column(
        Enum(PolicyStatus), nullable=False,
        default=PolicyStatus.DRAFT
    )
    content: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Contenido en Markdown"
    )
    policy_version: Mapped[str] = mapped_column(
        String(20), nullable=False, default="1.0"
    )
    applicable_frameworks: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment='["NIS2", "ENS", "ISO27001"]'
    )
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(
        DATETIME(fsp=6), nullable=True
    )
    review_due_at: Mapped[datetime | None] = mapped_column(
        DATETIME(fsp=6), nullable=True,
        comment="Fecha límite de próxima revisión"
    )
    # --- Campos IA ---
    ai_generated: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    ai_last_update_suggestion: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Última sugerencia de actualización de la IA"
    )
    requires_acknowledgment: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="¿Requiere confirmación de lectura?"
    )
    target_roles: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment='["all", "developers", "finance"]'
    )
