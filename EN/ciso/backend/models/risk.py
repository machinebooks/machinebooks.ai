# Chapter 7 — Risk management: MAGERIT, FAIR, ISO 27005 in one model
#
# A single relational structure supports 15+ risk methodologies.
# The `methodology` field conditions which taxonomies, scales, and
# catalogs are available, but the core chain is always:
#   Asset -> Threat -> Vulnerability -> RiskScenario -> Control -> Treatment

from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, BigInteger,
    ForeignKey, DateTime, JSON, Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

try:
    from backend.models.base import BaseModel
except ImportError:
    from base import BaseModel


# ── Enumerations ──────────────────────────────────────────────────────────

class RiskMethodology(str, PyEnum):
    """Supported risk analysis methodologies (all public documentation)."""
    MAGERIT_V3 = "magerit_v3"           # CCN, Spain — mandatory for ENS
    ISO_27005 = "iso_27005"             # ISO/IEC — complements ISO 27001
    NIST_SP_800_30 = "nist_sp_800_30"   # NIST, USA
    FAIR = "fair"                        # The Open Group — quantitative
    OCTAVE_ALLEGRO = "octave_allegro"   # Carnegie Mellon
    EBIOS_RM = "ebios_rm"              # ANSSI, France
    MEHARI = "mehari"                    # CLUSIF, France
    CRAMM = "cramm"                      # UK Government
    IT_GRUNDSCHUTZ = "it_grundschutz"   # BSI, Germany
    NIST_CSF = "nist_csf"              # NIST Cybersecurity Framework
    ISO_31000 = "iso_31000"             # ISO — generic risk management
    COBIT = "cobit"                      # ISACA
    CUSTOM = "custom"                    # User-defined methodology


class AssetType(str, PyEnum):
    """Asset types — superset covering all methodologies.
    MAGERIT defines [S],[D],[SW],[HW],[COM],[AUX],[L],[P].
    The methodology field filters which types are valid.
    """
    SERVICE = "service"           # [S] MAGERIT
    DATA = "data"                 # [D] MAGERIT
    SOFTWARE = "software"         # [SW] MAGERIT
    HARDWARE = "hardware"         # [HW] MAGERIT
    NETWORK = "network"           # [COM] MAGERIT
    AUXILIARY = "auxiliary"        # [AUX] MAGERIT
    FACILITY = "facility"         # [L] MAGERIT
    PERSONNEL = "personnel"       # [P] MAGERIT
    PROCESS = "process"           # ISO 27005
    INFORMATION = "information"   # ISO 27005
    THIRD_PARTY = "third_party"   # NIS2/DORA
    OTHER = "other"


class TreatmentStrategy(str, PyEnum):
    """Risk treatment strategies — ISO 31000."""
    MITIGATE = "mitigate"
    TRANSFER = "transfer"
    AVOID = "avoid"
    ACCEPT = "accept"


# ── Asset ─────────────────────────────────────────────────────────────────

class Asset(BaseModel):
    """Information asset — central entity of every risk analysis.

    Common across all methodologies. Valuation fields are conditional
    on the methodology of the parent analysis.
    """
    __tablename__ = "risk_assets"

    # Identification
    name = Column(String(255), nullable=False)
    code = Column(String(50), comment="Internal code: ACT-001")
    description = Column(Text)
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    owner = Column(String(255), comment="Asset owner")

    # Classification
    criticality = Column(Integer, default=3, comment="1-5 scale")

    # MAGERIT DICAT dimensions (only when methodology = MAGERIT_V3)
    val_disponibilidad = Column(Integer, comment="Availability 0-4")
    val_integridad = Column(Integer, comment="Integrity 0-4")
    val_confidencialidad = Column(Integer, comment="Confidentiality 0-4")
    val_autenticidad = Column(Integer, comment="Authenticity 0-4")
    val_trazabilidad = Column(Integer, comment="Traceability 0-4")

    # Generic valuation (ISO 27005, NIST, etc.)
    value_qualitative = Column(Integer, comment="Qualitative value 1-5")
    value_quantitative = Column(Float, comment="Economic value in EUR (FAIR)")

    # Metadata
    location = Column(String(255))
    classification = Column(String(50), comment="public | internal | confidential | secret")
    dependencies = Column(JSON, comment="IDs of assets this one depends on")

    # Relationships
    analysis_id = Column(BigInteger, ForeignKey("risk_analyses.id"), nullable=False)
    risk_scenarios = relationship("RiskScenario", back_populates="asset")


# ── RiskScenario ──────────────────────────────────────────────────────────

class RiskScenario(BaseModel):
    """Risk scenario — combination of asset + threat + vulnerability.

    The risk calculation depends on the methodology:
    - Qualitative (MAGERIT, ISO 27005, NIST): probability x impact (1-25)
    - Quantitative (FAIR): LEF x LM -> ALE in EUR
    """
    __tablename__ = "risk_scenarios"

    # Identification
    name = Column(String(255), nullable=False)
    code = Column(String(50), comment="SCN-001")
    description = Column(Text)

    # Relationships with asset and threat
    asset_id = Column(BigInteger, ForeignKey("risk_assets.id"), nullable=False)
    threat_id = Column(BigInteger, nullable=False, comment="FK to risk_threats")
    vulnerability_description = Column(Text)

    # --- Qualitative valuation (MAGERIT, ISO 27005, NIST, etc.) ---
    probability = Column(Integer, comment="1-5 scale")
    impact = Column(Integer, comment="1-5 scale")
    inherent_risk = Column(Integer, comment="probability x impact (1-25)")

    # MAGERIT DICAT impact dimensions
    impact_disponibilidad = Column(Integer, comment="Impact on Availability 0-4")
    impact_integridad = Column(Integer, comment="Impact on Integrity 0-4")
    impact_confidencialidad = Column(Integer, comment="Impact on Confidentiality 0-4")
    impact_autenticidad = Column(Integer, comment="Impact on Authenticity 0-4")
    impact_trazabilidad = Column(Integer, comment="Impact on Traceability 0-4")

    # --- Quantitative valuation — FAIR ---
    fair_lef = Column(Float, comment="Loss Event Frequency — events/year")
    fair_lm_primary = Column(Float, comment="Primary Loss Magnitude — EUR")
    fair_lm_secondary = Column(Float, comment="Secondary Loss Magnitude — EUR")
    fair_ale = Column(Float, comment="Annual Loss Expectancy = LEF x (LM_p + LM_s)")

    # --- Residual risk (after controls) ---
    residual_probability = Column(Integer, comment="Residual probability 1-5")
    residual_impact = Column(Integer, comment="Residual impact 1-5")
    residual_risk = Column(Integer, comment="residual_probability x residual_impact")
    residual_fair_ale = Column(Float, comment="Residual ALE after controls — EUR")

    # --- Treatment ---
    treatment_strategy = Column(SQLEnum(TreatmentStrategy))
    treatment_justification = Column(Text)
    risk_owner = Column(String(255))

    # Status
    status = Column(String(30), default="identified",
                    comment="identified | analyzed | treated | accepted | monitoring")
    review_date = Column(DateTime)

    # Relationships
    analysis_id = Column(BigInteger, ForeignKey("risk_analyses.id"), nullable=False)
    asset = relationship("Asset", back_populates="risk_scenarios")
    controls = relationship("RiskControl", back_populates="scenario",
                            cascade="all, delete-orphan")


# ── RiskControl ───────────────────────────────────────────────────────────

class RiskControl(BaseModel):
    """Control applied to mitigate a risk scenario.

    Links a risk scenario to a compliance control (Chapter 8)
    for cross-module traceability.
    """
    __tablename__ = "risk_controls"

    scenario_id = Column(BigInteger, ForeignKey("risk_scenarios.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    control_type = Column(String(50), comment="preventive | detective | corrective")
    implementation_status = Column(String(30), default="planned",
                                   comment="planned | in_progress | implemented | verified")

    # Link to compliance control (Chapter 8) for cross-module mapping
    compliance_control_id = Column(BigInteger, nullable=True,
                                   comment="FK to compliance_controls for traceability")

    # Effectiveness assessment
    effectiveness = Column(Integer, comment="Estimated effectiveness 1-5")
    probability_reduction = Column(Integer, default=0, comment="How much it reduces probability")
    impact_reduction = Column(Integer, default=0, comment="How much it reduces impact")

    # Relationships
    scenario = relationship("RiskScenario", back_populates="controls")
