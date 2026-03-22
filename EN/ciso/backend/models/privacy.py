# Chapter 4 — DataProcessingActivity (Art. 30 GDPR)
# Chapter 6 — DataBreach (Art. 33-34 GDPR)
#
# These models translate GDPR articles into typed SQLAlchemy columns.
# Every field is commented with the regulation it implements.

from enum import Enum as PyEnum
from datetime import datetime, timedelta

from sqlalchemy import (
    Column, String, Text, Boolean, BigInteger, Integer,
    ForeignKey, DateTime, JSON, Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

# In a real project this import resolves to the shared BaseModel (Chapter 3).
# Here we reference it for structural clarity.
try:
    from backend.models.base import BaseModel
except ImportError:
    from base import BaseModel


# ── Art. 6.1 GDPR — Legal bases (closed set, no seventh option) ──────────

class LegalBasis(str, PyEnum):
    """The six legal bases for data processing under Art. 6.1 GDPR."""
    CONSENT = "consent"                    # Art. 6.1.a
    CONTRACT = "contract"                  # Art. 6.1.b
    LEGAL_OBLIGATION = "legal_obligation"  # Art. 6.1.c
    VITAL_INTEREST = "vital_interest"      # Art. 6.1.d
    PUBLIC_INTEREST = "public_interest"    # Art. 6.1.e
    LEGITIMATE_INTEREST = "legitimate_interest"  # Art. 6.1.f


class TransferSafeguard(str, PyEnum):
    """Art. 46 GDPR — Safeguards for international transfers."""
    ADEQUACY_DECISION = "adequacy"     # Art. 45
    STANDARD_CLAUSES = "scc"           # Art. 46.2.c
    BINDING_RULES = "bcr"              # Art. 47
    CERTIFICATION = "certification"    # Art. 42
    DEROGATION_49 = "derogation_49"    # Art. 49


# ── DataProcessingActivity ────────────────────────────────────────────────

class DataProcessingActivity(BaseModel):
    """Record of Processing Activity (Art. 30.1 GDPR).

    Each field maps to a specific paragraph of Article 30.
    Inherits multi-tenancy, audit, soft delete from BaseModel (Chapter 3).
    """
    __tablename__ = "data_processing_activities"

    # --- Identification ---
    name = Column(String(255), nullable=False, comment="Treatment name")
    description = Column(Text, comment="Treatment description")
    code = Column(String(50), unique=True, comment="Internal code: RAT-001")
    status = Column(String(20), default="active")  # active | suspended | archived

    # --- Art. 30.1.a — Controller and DPO ---
    controller_name = Column(String(255), nullable=False,
                             comment="Data controller name")
    controller_contact = Column(String(255))
    joint_controller = Column(String(255), nullable=True,
                              comment="Art. 26 GDPR — Joint controller if applicable")
    dpo_name = Column(String(255), comment="DPO name")
    dpo_contact = Column(String(255), comment="DPO contact")

    # --- Art. 30.1.b — Purposes and legal basis ---
    purposes = Column(JSON, nullable=False,
                      comment='Purposes: ["HR management", "payroll"]')
    legal_basis = Column(SQLEnum(LegalBasis), nullable=False,
                         comment="Legal basis under Art. 6.1 GDPR")
    legal_basis_detail = Column(Text,
                                comment="Specific justification for the legal basis")

    # --- Art. 30.1.c — Categories of data subjects and data ---
    data_subject_categories = Column(JSON,
                                     comment='["employees", "clients", "suppliers"]')
    personal_data_categories = Column(JSON,
                                      comment='["identification", "contact", "financial"]')
    special_categories = Column(Boolean, default=False,
                                comment="Art. 9 — Special category data?")
    special_categories_detail = Column(JSON,
                                       comment='["health", "biometric"]')

    # --- Art. 30.1.d — Recipients ---
    recipients = Column(JSON, comment="Categories of data recipients")

    # --- Art. 30.1.e — International transfers ---
    international_transfers = Column(Boolean, default=False)
    transfer_countries = Column(JSON, comment='["US", "UK"]')
    transfer_safeguards = Column(SQLEnum(TransferSafeguard), nullable=True)
    transfer_safeguards_detail = Column(Text)

    # --- Art. 30.1.f — Retention periods ---
    retention_period = Column(String(255),
                              comment="e.g. '5 years', '6 months after contract end'")
    retention_criteria = Column(Text)

    # --- Art. 30.1.g — Security measures (Art. 32) ---
    security_measures = Column(JSON,
                               comment='["encryption_at_rest", "access_control", "backup"]')

    # --- Operational fields ---
    department_id = Column(BigInteger, nullable=True)
    risk_level = Column(String(20), comment="low | medium | high | very_high")
    dpia_required = Column(Boolean, default=False, comment="Art. 35 — DPIA required?")

    # --- Lifecycle ---
    last_review_date = Column(DateTime, comment="Last DPO review")
    next_review_date = Column(DateTime, comment="Next scheduled review")


# ── DataBreach ────────────────────────────────────────────────────────────

class BreachStatus(str, PyEnum):
    """Lifecycle states — controlled transitions only."""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    ASSESSED = "assessed"
    NOTIFIED_AUTHORITY = "notified_authority"   # Art. 33
    NOTIFIED_SUBJECTS = "notified_subjects"     # Art. 34
    CLOSED = "closed"


class BreachSeverity(str, PyEnum):
    """Severity levels based on DPA criteria."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BreachType(str, PyEnum):
    """Classification by data impact type."""
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    AVAILABILITY = "availability"
    MIXED = "mixed"


# Valid state transitions — prevents illegal jumps in the lifecycle
VALID_TRANSITIONS: dict[BreachStatus, list[BreachStatus]] = {
    BreachStatus.DETECTED: [BreachStatus.INVESTIGATING],
    BreachStatus.INVESTIGATING: [BreachStatus.ASSESSED],
    BreachStatus.ASSESSED: [
        BreachStatus.NOTIFIED_AUTHORITY,
        BreachStatus.CLOSED,
    ],
    BreachStatus.NOTIFIED_AUTHORITY: [
        BreachStatus.NOTIFIED_SUBJECTS,
        BreachStatus.CLOSED,
    ],
    BreachStatus.NOTIFIED_SUBJECTS: [BreachStatus.CLOSED],
    BreachStatus.CLOSED: [],  # Terminal state
}


class DataBreach(BaseModel):
    """Data breach record (Art. 33-34 GDPR).

    The notification_deadline is auto-calculated as detected_at + 72 hours.
    The state machine enforces valid transitions only.
    """
    __tablename__ = "data_breaches"

    # --- Identification ---
    code = Column(String(50), unique=True, nullable=False,
                  comment="Code: BREACH-2025-001")
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # --- Classification ---
    breach_type = Column(SQLEnum(BreachType), nullable=False)
    severity = Column(SQLEnum(BreachSeverity), nullable=False)
    status = Column(SQLEnum(BreachStatus), default=BreachStatus.DETECTED)

    # --- Timing (Art. 33.1 — 72 hours) ---
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notification_deadline = Column(DateTime, nullable=False,
                                   comment="detected_at + 72h — auto-calculated")
    notified_authority_at = Column(DateTime, nullable=True)
    notified_subjects_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # --- Impact (Art. 33.3) ---
    affected_count = Column(Integer, nullable=True,
                            comment="Estimated number of affected data subjects")
    data_categories_affected = Column(JSON)
    special_categories_affected = Column(Boolean, default=False)

    # --- Response ---
    root_cause = Column(Text)
    measures_taken = Column(JSON)
    measures_proposed = Column(JSON)

    # --- Authority notification ---
    authority_reference = Column(String(100), nullable=True,
                                comment="DPA case reference number")
    notify_subjects_required = Column(Boolean, default=False,
                                      comment="Art. 34 — Must notify data subjects?")

    # --- Responsible parties ---
    reported_by = Column(BigInteger, nullable=True)
    dpo_id = Column(BigInteger, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-calculate the 72-hour notification deadline
        if self.detected_at and not self.notification_deadline:
            self.notification_deadline = self.detected_at + timedelta(hours=72)

    def can_transition_to(self, new_status: BreachStatus) -> bool:
        """Check if a state transition is valid."""
        return new_status in VALID_TRANSITIONS.get(self.status, [])

    @property
    def hours_remaining(self) -> float:
        """Hours remaining before the notification deadline."""
        if self.notified_authority_at:
            return 0.0
        delta = self.notification_deadline - datetime.utcnow()
        return max(0.0, delta.total_seconds() / 3600)

    @property
    def is_overdue(self) -> bool:
        """True if the 72-hour deadline has passed without notification."""
        if self.notified_authority_at:
            return False
        return datetime.utcnow() > self.notification_deadline
