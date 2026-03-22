# Chapter 8 — Compliance frameworks: ENS, ISO 27001, ISO 27701
#
# A unified model where all controls from all frameworks live in the
# same structure. Cross-framework mapping lets a single piece of evidence
# satisfy equivalent controls across ENS, ISO 27001, and ISO 27701.

import enum

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    Enum as SAEnum, JSON, UniqueConstraint,
)
from sqlalchemy.orm import relationship

try:
    from backend.models.base import BaseModel
except ImportError:
    from base import BaseModel


# ── Enumerations ──────────────────────────────────────────────────────────

class FrameworkCategory(str, enum.Enum):
    NATIONAL = "national"            # ENS, CCN-STIC
    INTERNATIONAL = "international"  # ISO 27001, ISO 27701
    EUROPEAN = "european"            # NIS2, DORA, AI Act
    SECTORIAL = "sectorial"          # PCI-DSS, HIPAA


class ComplianceStatus(str, enum.Enum):
    """Compliance assessment status (auditor/CISO perspective)."""
    NOT_ASSESSED = "not_assessed"
    NOT_APPLICABLE = "not_applicable"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    COMPLIANT = "compliant"


class ImplementationStatus(str, enum.Enum):
    """Technical implementation progress."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"


class EvidenceType(str, enum.Enum):
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    CONFIGURATION = "configuration"
    LOG = "log"
    CERTIFICATE = "certificate"
    TEST_RESULT = "test_result"


# ── ComplianceFramework ───────────────────────────────────────────────────

class ComplianceFramework(BaseModel):
    """Regulatory framework: ENS, ISO 27001, ISO 27701, NIS2, DORA, AI Act.

    Pre-loaded as seed data — the controls are public documentation.
    """
    __tablename__ = "compliance_frameworks"

    code = Column(String(50), nullable=False, unique=True)  # "ENS", "ISO27001"
    name = Column(String(200), nullable=False)
    version = Column(String(50), nullable=False)            # "RD 311/2022", "2022"
    category = Column(SAEnum(FrameworkCategory), nullable=False)
    description = Column(Text)
    official_url = Column(String(500))
    total_controls = Column(Integer, default=0)
    is_active = Column(Integer, default=1)

    controls = relationship(
        "ComplianceControl",
        back_populates="framework",
        cascade="all, delete-orphan",
    )


# ── ComplianceControl ─────────────────────────────────────────────────────

class ComplianceControl(BaseModel):
    """Individual control within a framework.

    Supports hierarchy via parent_id:
    - ENS: org -> org.1 -> org.1.a
    - ISO 27001: Organizational -> A.5.1
    """
    __tablename__ = "compliance_controls"

    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("compliance_controls.id"), nullable=True)

    code = Column(String(50), nullable=False)       # "mp.com.2", "A.8.24"
    name = Column(String(300), nullable=False)
    description = Column(Text)
    guidance = Column(Text, comment="Implementation guidance")
    level = Column(Integer, default=0, comment="Hierarchy level: 0=category, 1=control")

    # Compliance assessment (auditor/CISO)
    compliance_status = Column(
        SAEnum(ComplianceStatus), default=ComplianceStatus.NOT_ASSESSED,
    )
    # Technical implementation progress
    implementation_status = Column(
        SAEnum(ImplementationStatus), default=ImplementationStatus.NOT_STARTED,
    )
    not_applicable_justification = Column(Text)

    # ENS: differentiated requirements by system category
    # {"BASICA": "applies", "MEDIA": "applies+", "ALTA": "reinforced"}
    level_requirements = Column(JSON, nullable=True)

    # Relationships
    framework = relationship("ComplianceFramework", back_populates="controls")
    parent = relationship("ComplianceControl", remote_side="ComplianceControl.id",
                          backref="children")
    evidences = relationship("Evidence", back_populates="control",
                             cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("framework_id", "code", name="uq_framework_control"),
    )


# ── Evidence ──────────────────────────────────────────────────────────────

class Evidence(BaseModel):
    """Evidence linked to a compliance control.

    A single evidence (e.g., TLS configuration screenshot) can be linked
    to equivalent controls across ENS, ISO 27001, and ISO 27701 via
    cross-framework mapping.
    """
    __tablename__ = "compliance_evidences"

    control_id = Column(Integer, ForeignKey("compliance_controls.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    evidence_type = Column(SAEnum(EvidenceType), nullable=False)
    file_path = Column(String(500))
    file_hash = Column(String(128), comment="SHA-256 for integrity verification")
    collected_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=True, comment="Evidence expiration date")
    collected_by = Column(String(200))
    is_valid = Column(Integer, default=1)

    control = relationship("ComplianceControl", back_populates="evidences")


# ── Cross-framework mapping ──────────────────────────────────────────────

class ControlMapping(BaseModel):
    """Maps equivalent controls across different frameworks.

    Example: ENS mp.com.2 <-> ISO 27001 A.8.24 <-> ISO 27701 A.7.4.5
    When one is marked compliant, the system suggests updating the mapped ones.
    """
    __tablename__ = "control_mappings"

    source_control_id = Column(Integer, ForeignKey("compliance_controls.id"), nullable=False)
    target_control_id = Column(Integer, ForeignKey("compliance_controls.id"), nullable=False)
    mapping_type = Column(String(50), default="equivalent",
                          comment="equivalent | partial | related")
    notes = Column(Text)

    __table_args__ = (
        UniqueConstraint("source_control_id", "target_control_id",
                         name="uq_control_mapping"),
    )
