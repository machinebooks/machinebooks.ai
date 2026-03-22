# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/models.py

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    Enum as SAEnum, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel  # Incluye tenant_id, audit fields

import enum

class FrameworkCategory(str, enum.Enum):
    NATIONAL = "national"        # ENS, CCN-STIC
    INTERNATIONAL = "international"  # ISO 27001, ISO 27701
    EUROPEAN = "european"        # NIS2, DORA, AI Act
    SECTORIAL = "sectorial"      # PCI-DSS, HIPAA

class ComplianceStatus(str, enum.Enum):
    NOT_ASSESSED = "not_assessed"
    NOT_APPLICABLE = "not_applicable"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    COMPLIANT = "compliant"

class ImplementationStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"

class ComplianceFramework(BaseModel):
    """Marco de cumplimiento: ENS, ISO 27001, ISO 27701, etc."""
    __tablename__ = "compliance_frameworks"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True)  # "ENS", "ISO27001"
    name = Column(String(200), nullable=False)
    version = Column(String(50), nullable=False)  # "RD 311/2022", "2022"
    category = Column(SAEnum(FrameworkCategory), nullable=False)
    description = Column(Text)
    official_url = Column(String(500))  # Enlace a BOE, ISO, etc.
    total_controls = Column(Integer, default=0)
    is_active = Column(Integer, default=1)

    # Relación con controles
    controls = relationship(
        "ComplianceControl",
        back_populates="framework",
        cascade="all, delete-orphan"
    )
