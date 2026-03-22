# Extraído de: LibroCISO/cap-04-registro-tratamientos.md
# Modelo de Tratamiento — diseñado desde el Art. 30.1 RGPD
# Cada campo mapea a un requisito legal específico

from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Text, Boolean, BigInteger,
    ForeignKey, DateTime, JSON, Enum as SQLEnum
)
from app.models.base import BaseModel  # multi-tenant, audit, soft delete


class LegalBasis(str, PyEnum):
    """Art. 6.1 RGPD — Las seis bases jurídicas posibles.

    Conjunto cerrado: no existe séptima opción.
    La LOPDGDD matiza algunas, pero no amplía el conjunto.
    """
    CONSENT = "consent"                    # Art. 6.1.a — Consentimiento
    CONTRACT = "contract"                  # Art. 6.1.b — Ejecución contractual
    LEGAL_OBLIGATION = "legal_obligation"  # Art. 6.1.c — Obligación legal
    VITAL_INTEREST = "vital_interest"      # Art. 6.1.d — Intereses vitales
    PUBLIC_INTEREST = "public_interest"    # Art. 6.1.e — Interés público
    LEGITIMATE_INTEREST = "legitimate_interest"  # Art. 6.1.f — Interés legítimo


class TransferSafeguard(str, PyEnum):
    """Art. 46 RGPD — Garantías para transferencias internacionales."""
    ADEQUACY_DECISION = "adequacy"     # Art. 45 — Decisión de adecuación
    STANDARD_CLAUSES = "scc"           # Art. 46.2.c — Cláusulas tipo
    BINDING_RULES = "bcr"              # Art. 47 — Normas corporativas vinculantes
    CERTIFICATION = "certification"     # Art. 42 — Mecanismo de certificación
    DEROGATION_49 = "derogation_49"    # Art. 49 — Excepciones tasadas


class DataProcessingActivity(BaseModel):
    """Registro de Actividad de Tratamiento (Art. 30.1 RGPD).

    Cada campo corresponde a un apartado del artículo.
    Multi-tenant: aislado por corporate_id (heredado de BaseModel).
    Versionado: soft delete + optimistic locking heredados.
    """
    __tablename__ = "data_processing_activities"

    # --- Identificación del tratamiento ---
    name = Column(String(255), nullable=False, comment="Nombre del tratamiento")
    description = Column(Text, comment="Descripción del tratamiento")
    code = Column(String(50), unique=True, comment="Código interno: RAT-001")
    status = Column(String(20), default="active")  # active, suspended, archived

    # --- Art. 30.1.a — Responsable y DPO ---
    controller_name = Column(String(255), nullable=False,
                             comment="Nombre del responsable del tratamiento")
    controller_contact = Column(String(255),
                                comment="Email/teléfono del responsable")
    joint_controller = Column(String(255), nullable=True,
                              comment="Art. 26 RGPD — Corresponsable, si aplica")
    dpo_name = Column(String(255), comment="Nombre del DPO")
    dpo_contact = Column(String(255), comment="Contacto del DPO")

    # --- Art. 30.1.b — Finalidades y base jurídica ---
    purposes = Column(JSON, nullable=False,
                      comment='Finalidades: ["gestión RRHH", "nóminas"]')
    legal_basis = Column(SQLEnum(LegalBasis), nullable=False,
                         comment="Base jurídica Art. 6.1 RGPD")
    legal_basis_detail = Column(Text,
                                comment="Justificación específica de la base")

    # --- Art. 30.1.c — Categorías de interesados y datos ---
    data_subject_categories = Column(
        JSON, comment='["empleados", "clientes", "proveedores"]')
    personal_data_categories = Column(
        JSON, comment='["identificativos", "contacto", "financieros"]')
    special_categories = Column(
        Boolean, default=False, comment="Art. 9 — ¿Datos sensibles?")
    special_categories_detail = Column(
        JSON, comment='["salud", "biométricos"] — Solo si special_categories=True')

    # --- Art. 30.1.d — Destinatarios ---
    recipients = Column(
        JSON, comment='Categorías de destinatarios de los datos')

    # --- Art. 30.1.e — Transferencias internacionales ---
    international_transfers = Column(
        Boolean, default=False, comment="¿Hay transferencias a terceros países?")
    transfer_countries = Column(
        JSON, comment='["US", "UK"] — Países destino')
    transfer_safeguards = Column(
        SQLEnum(TransferSafeguard), nullable=True,
        comment="Art. 46 — Tipo de garantía")
    transfer_safeguards_detail = Column(
        Text, comment="Detalle de las garantías aplicadas")

    # --- Art. 30.1.f — Plazos de conservación ---
    retention_period = Column(
        String(255), comment="Plazo: '5 años', '6 meses tras fin contrato'")
    retention_criteria = Column(
        Text, comment="Criterio legal o de negocio para el plazo")

    # --- Art. 30.1.g — Medidas de seguridad (Art. 32 RGPD) ---
    security_measures = Column(
        JSON, comment='["cifrado_reposo", "control_acceso", "backup"]')

    # --- Campos operativos (no Art. 30, pero necesarios) ---
    department_id = Column(BigInteger, ForeignKey("departments.id"),
                           comment="Departamento responsable")
    system_id = Column(BigInteger, ForeignKey("information_systems.id"),
                       nullable=True, comment="Sistema de información asociado")
    risk_level = Column(String(20),
                        comment="low, medium, high, very_high")
    dpia_required = Column(Boolean, default=False,
                           comment="Art. 35 — ¿Requiere DPIA?")
    dpia_id = Column(BigInteger, ForeignKey("dpias.id"), nullable=True,
                     comment="DPIA asociada, si existe")

    # --- Ciclo de vida ---
    last_review_date = Column(DateTime, comment="Última revisión del DPO")
    next_review_date = Column(DateTime, comment="Próxima revisión programada")
    review_notes = Column(Text, comment="Notas de la última revisión")

    # --- Relaciones ---
    # department = relationship("Department", back_populates="processing_activities")
    # processors = relationship("DataProcessor", secondary="activity_processors")
    # evidences = relationship("Evidence", back_populates="processing_activity")
