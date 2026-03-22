# Extraído de: LibroCISO/cap-05-dpia-derechos.md
# Modelo DPIA — diseñado desde el Art. 35 RGPD
# Cada sección corresponde a un apartado del Art. 35.7

from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Text, Boolean, BigInteger,
    ForeignKey, DateTime, JSON, Enum as SQLEnum
)
from app.models.base import BaseModel  # multi-tenant, audit, soft delete


class DPIAStatus(str, PyEnum):
    """Estados de la DPIA según ciclo de vida regulatorio."""
    DRAFT = "draft"                          # Borrador inicial
    UNDER_REVIEW = "under_review"            # En revisión por el DPO
    APPROVED = "approved"                    # Aprobada — tratamiento puede proceder
    PRIOR_CONSULTATION = "prior_consultation"  # Art. 36 — Consulta previa a la AEPD
    REJECTED = "rejected"                    # Rechazada — tratamiento no puede proceder


class SectionStatus(str, PyEnum):
    """Estado de cada sección individual de la DPIA."""
    EMPTY = "empty"                # Sin contenido
    DRAFT = "draft"                # Borrador generado (por agente o manual)
    REVIEWED = "reviewed"          # Revisada por el DPO
    APPROVED = "approved"          # Aprobada por el DPO
    NEEDS_REVISION = "needs_revision"  # Devuelta para corrección


class DPIA(BaseModel):
    """Evaluación de Impacto en la Protección de Datos (Art. 35 RGPD).

    Vinculada a uno o más tratamientos del RAT (Cap. 4).
    Hereda del BaseModel común (Capítulo 3): multi-tenant, audit, soft delete.
    """
    __tablename__ = "dpias"

    # --- Identificación ---
    title = Column(String(255), nullable=False,
                   comment="Título descriptivo de la DPIA")
    code = Column(String(50), unique=True,
                  comment="Código interno: DPIA-2026-001")
    status = Column(SQLEnum(DPIAStatus), default=DPIAStatus.DRAFT,
                    comment="Estado global de la DPIA")

    # --- Vinculación con tratamiento(s) ---
    primary_activity_id = Column(
        BigInteger, ForeignKey("data_processing_activities.id"),
        nullable=False,
        comment="Tratamiento principal que origina la DPIA")

    # --- Art. 35.7.a — Descripción sistemática del tratamiento ---
    description_content = Column(
        Text, comment="Descripción de operaciones y fines del tratamiento")
    description_status = Column(
        SQLEnum(SectionStatus), default=SectionStatus.EMPTY)
    description_reviewed_at = Column(DateTime, nullable=True)
    description_reviewed_by = Column(BigInteger, nullable=True)

    # --- Art. 35.7.b — Necesidad y proporcionalidad ---
    necessity_content = Column(
        Text, comment="Evaluación de necesidad y proporcionalidad")
    necessity_status = Column(
        SQLEnum(SectionStatus), default=SectionStatus.EMPTY)
    necessity_reviewed_at = Column(DateTime, nullable=True)
    necessity_reviewed_by = Column(BigInteger, nullable=True)

    # --- Art. 35.7.c — Riesgos para los derechos y libertades ---
    risks_content = Column(
        Text, comment="Evaluación de riesgos identificados")
    risks_identified = Column(
        JSON, comment='Lista de riesgos: [{"risk": "...", "likelihood": "...", "impact": "..."}]')
    risks_status = Column(
        SQLEnum(SectionStatus), default=SectionStatus.EMPTY)
    risks_reviewed_at = Column(DateTime, nullable=True)
    risks_reviewed_by = Column(BigInteger, nullable=True)

    # --- Art. 35.7.d — Medidas de mitigación ---
    measures_content = Column(
        Text, comment="Medidas previstas para afrontar los riesgos")
    measures_proposed = Column(
        JSON, comment='[{"measure": "...", "risk_addressed": "...", "status": "planned|implemented"}]')
    measures_status = Column(
        SQLEnum(SectionStatus), default=SectionStatus.EMPTY)
    measures_reviewed_at = Column(DateTime, nullable=True)
    measures_reviewed_by = Column(BigInteger, nullable=True)

    # --- Criterios GT29/EDPB que se cumplen ---
    gt29_criteria = Column(
        JSON, comment='Criterios cumplidos: ["scoring", "automated_decisions", ...]')
    gt29_criteria_count = Column(
        BigInteger, default=0,
        comment="Número de criterios GT29 cumplidos (>=2 → DPIA obligatoria)")

    # --- Resultado y aprobación ---
    residual_risk_level = Column(
        String(20), comment="low, medium, high, very_high")
    dpo_opinion = Column(Text, comment="Opinión formal del DPO")
    dpo_approved_at = Column(DateTime, nullable=True)
    dpo_approved_by = Column(BigInteger, nullable=True)
    requires_prior_consultation = Column(
        Boolean, default=False,
        comment="Art. 36 — ¿Requiere consulta previa a la AEPD?")

    # --- Ciclo de vida ---
    initiated_at = Column(DateTime, comment="Fecha de inicio de la DPIA")
    completed_at = Column(DateTime, nullable=True,
                          comment="Fecha de finalización")
    next_review_date = Column(DateTime, nullable=True,
                              comment="Próxima revisión programada")
