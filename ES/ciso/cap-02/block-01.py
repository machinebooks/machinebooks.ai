# Extraído de: LibroCISO/cap-02-arquitecto-ia-regulatorio.md
# Modelo didáctico basado en Art. 30.1 RGPD
# Ejemplo didáctico: patrones/privacidad/data_processing_activity.py

from sqlalchemy import Column, String, Text, JSON, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

class LegalBasis(enum.Enum):
    """Art. 6.1 RGPD — Bases jurídicas del tratamiento."""
    CONSENT = "consentimiento"                    # Art. 6.1.a
    CONTRACT = "ejecución de contrato"            # Art. 6.1.b
    LEGAL_OBLIGATION = "obligación legal"         # Art. 6.1.c
    VITAL_INTERESTS = "intereses vitales"         # Art. 6.1.d
    PUBLIC_INTEREST = "interés público"           # Art. 6.1.e
    LEGITIMATE_INTEREST = "interés legítimo"      # Art. 6.1.f

class DataProcessingActivity(BaseModel):
    """Registro de Actividades de Tratamiento — Art. 30.1 RGPD.

    Cada campo mapea a un apartado específico del artículo.
    Los campos heredados de BaseModel proporcionan:
    - id (UUID), created_at, updated_at, deleted_at (soft delete)
    - created_by (usuario que crea el registro)
    - corporate_id (multi-tenancy obligatorio)
    """
    __tablename__ = "data_processing_activities"

    # --- Art. 30.1.a — Responsable y contactos ---
    name = Column(String(255), nullable=False,
                  comment="Nombre del tratamiento")
    controller_name = Column(String(255), nullable=False,
                             comment="Nombre del responsable del tratamiento")
    controller_contact = Column(String(255),
                                comment="Datos de contacto del responsable")
    joint_controller = Column(String(255),
                              comment="Corresponsable, si aplica")
    dpo_contact = Column(String(255),
                         comment="Datos de contacto del DPO")

    # --- Art. 30.1.b — Finalidades del tratamiento ---
    purposes = Column(JSON, nullable=False,
                      comment="Array de finalidades del tratamiento")
    legal_basis = Column(SAEnum(LegalBasis), nullable=False,
                         comment="Base jurídica según Art. 6.1 RGPD")
    legal_basis_detail = Column(Text,
                                comment="Detalle: norma, contrato o interés concreto")

    # --- Art. 30.1.c — Categorías de interesados y datos ---
    data_subject_categories = Column(JSON,
        comment="Categorías de interesados: empleados, clientes, proveedores...")
    personal_data_categories = Column(JSON,
        comment="Categorías de datos: identificativos, financieros, salud...")

    # Art. 9 — Categorías especiales de datos
    special_categories = Column(Boolean, default=False,
        comment="¿Incluye datos del Art. 9? Salud, biométricos, ideología...")
    special_categories_detail = Column(Text,
        comment="Si special_categories=True, qué categorías y base del Art. 9.2")

    # --- Art. 30.1.d — Destinatarios ---
    recipients = Column(JSON,
        comment="Categorías de destinatarios de los datos")

    # --- Art. 30.1.e — Transferencias internacionales ---
    international_transfers = Column(Boolean, default=False,
        comment="¿Hay transferencia fuera del EEE?")
    transfer_countries = Column(JSON,
        comment="Países destino de transferencia")
    transfer_safeguards = Column(String(100),
        comment="Garantía Art. 46: CCT, decisión adecuación, BCR...")

    # --- Art. 30.1.f — Plazos de conservación ---
    retention_period = Column(String(255),
        comment="Plazo previsto para la supresión")
    retention_criteria = Column(Text,
        comment="Criterio de conservación si el plazo no es fijo")

    # --- Art. 30.1.g — Medidas de seguridad (Art. 32) ---
    security_measures = Column(JSON,
        comment="Descripción de medidas técnicas y organizativas")

    # --- Campos operativos (no exigidos por Art. 30 pero necesarios) ---
    status = Column(String(20), default="draft",
        comment="Estado: draft, active, under_review, archived")
    department = Column(String(100),
        comment="Departamento responsable del tratamiento")
    last_review_date = Column(DateTime,
        comment="Fecha de última revisión del registro")

    # Relaciones
    risks = relationship("ProcessingRisk", back_populates="processing_activity")
    evidences = relationship("ProcessingEvidence", back_populates="processing_activity")
