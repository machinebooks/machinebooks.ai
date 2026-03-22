# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import (
    Column, String, Text, DateTime, Integer,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ExceptionStatus(str, Enum):
    REQUESTED = "requested"       # Solicitud enviada
    UNDER_REVIEW = "under_review" # Agente evaluando riesgo
    APPROVED = "approved"         # Aprobada por security lead
    DENIED = "denied"             # Denegada
    EXPIRED = "expired"           # Fecha de expiración superada
    RESOLVED = "resolved"         # Vulnerabilidad remediada


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SecurityException(Base):
    """Cada excepción vincula un hallazgo con una decisión de riesgo."""
    __tablename__ = "security_exceptions"

    id = Column(Integer, primary_key=True)
    finding_id = Column(String(128), nullable=False, index=True)
    finding_source = Column(String(64), nullable=False)  # semgrep, grype, trivy
    severity = Column(SAEnum(Severity), nullable=False)
    cve_id = Column(String(32), nullable=True)           # CVE-2024-XXXXX
    affected_component = Column(String(256), nullable=False)
    service_name = Column(String(128), nullable=False)

    # Solicitud
    requested_by = Column(String(128), nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow)
    business_justification = Column(Text, nullable=False)
    technical_justification = Column(Text, nullable=False)

    # Evaluación del agente
    agent_risk_score = Column(Integer, nullable=True)     # 0-100
    agent_assessment = Column(Text, nullable=True)
    compensating_controls = Column(JSON, nullable=True)   # Lista de controles sugeridos

    # Aprobación
    status = Column(SAEnum(ExceptionStatus), default=ExceptionStatus.REQUESTED)
    approved_by = Column(String(128), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    denial_reason = Column(Text, nullable=True)

    # Vigencia
    expires_at = Column(DateTime, nullable=False)
    max_renewals = Column(Integer, default=2)
    renewal_count = Column(Integer, default=0)

    # Resolución
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    reviews = relationship("ExceptionReview", back_populates="exception")
