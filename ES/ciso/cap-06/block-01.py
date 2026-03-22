# Extraído de: LibroCISO/cap-06-brechas-encargados-transferencias.md
# Modelo de Encargado de Tratamiento — Art. 28 RGPD
# Incluye evaluación periódica y seguimiento contractual

from sqlalchemy import (
    Column, String, Text, Boolean, BigInteger,
    ForeignKey, DateTime, JSON, Enum as SQLEnum, Float
)
from app.models.base import BaseModel


class ProcessorStatus(str, PyEnum):
    """Estado del encargado en el ciclo de gestión."""
    ACTIVE = "active"                 # Contrato vigente y evaluación al día
    PENDING_REVIEW = "pending_review" # Evaluación pendiente o vencida
    SUSPENDED = "suspended"           # Suspendido por incumplimiento
    TERMINATED = "terminated"         # Relación finalizada


class DataProcessor(BaseModel):
    """Encargado de tratamiento (Art. 28 RGPD).

    Cada encargado tiene una ficha, una evaluación periódica
    y un contrato vinculado. Se relaciona con uno o varios
    tratamientos del registro de actividades (Cap. 4).
    """
    __tablename__ = "data_processors"

    # --- Identificación del encargado ---
    name = Column(String(255), nullable=False,
                  comment="Razón social del encargado")
    tax_id = Column(String(50), comment="CIF/NIF del encargado")
    country = Column(String(3), default="ES",
                     comment="País del encargado (código ISO 3166-1)")
    contact_name = Column(String(255),
                          comment="Persona de contacto")
    contact_email = Column(String(255),
                           comment="Email de contacto")
    dpo_name = Column(String(255), nullable=True,
                      comment="DPO del encargado, si lo tiene")
    dpo_contact = Column(String(255), nullable=True,
                         comment="Contacto del DPO del encargado")

    # --- Estado y clasificación ---
    status = Column(SQLEnum(ProcessorStatus),
                    default=ProcessorStatus.PENDING_REVIEW)
    risk_level = Column(String(20), default="medium",
                        comment="Nivel de riesgo: low, medium, high, critical")
    services_description = Column(Text,
                                  comment="Descripción de los servicios prestados")
    data_categories_processed = Column(
        JSON, comment='Categorías de datos que trata')
    special_categories = Column(
        Boolean, default=False,
        comment="¿Trata datos del Art. 9?")

    # --- Contrato (Art. 28.3) ---
    contract_signed = Column(Boolean, default=False,
                             comment="¿Contrato de encargo firmado?")
    contract_date = Column(DateTime, nullable=True,
                           comment="Fecha de firma del contrato")
    contract_expiry = Column(DateTime, nullable=True,
                             comment="Fecha de vencimiento del contrato")
    contract_reference = Column(String(255), nullable=True,
                                comment="Referencia del documento de contrato")
    contract_compliant_art28 = Column(
        Boolean, default=False,
        comment="¿El contrato cumple todos los requisitos del Art. 28.3?")

    # --- Sub-encargados (Art. 28.2 y 28.4) ---
    has_sub_processors = Column(Boolean, default=False,
                                comment="¿Recurre a sub-encargados?")
    sub_processors = Column(
        JSON, nullable=True,
        comment='Lista de sub-encargados autorizados')
    sub_processor_authorization = Column(
        String(20), default="specific",
        comment="Tipo de autorización: specific o general (Art. 28.2)")

    # --- Evaluación periódica ---
    last_evaluation_date = Column(DateTime, nullable=True)
    last_evaluation_score = Column(Float, nullable=True,
                                   comment="Puntuación 0-100 del cuestionario")
    next_review_date = Column(DateTime, nullable=True,
                              comment="Próxima revisión programada")
    evaluation_notes = Column(Text, nullable=True)

    # --- Transferencias internacionales ---
    international_transfer = Column(
        Boolean, default=False,
        comment="¿El encargado transfiere datos fuera del EEE?")
    transfer_countries = Column(JSON, nullable=True)
    transfer_safeguard = Column(String(50), nullable=True,
                                comment="Tipo de garantía: adequacy, scc, bcr...")
