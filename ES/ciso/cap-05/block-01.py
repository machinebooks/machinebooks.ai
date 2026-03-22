# Extraído de: LibroCISO/cap-05-dpia-derechos.md
# Modelo de Solicitud de Derechos — diseñado desde Art. 15-22 RGPD
# Workflow con plazos legales como restricciones de diseño

from datetime import datetime, timedelta
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Text, Boolean, BigInteger,
    ForeignKey, DateTime, JSON, Enum as SQLEnum, Date
)
from app.models.base import BaseModel


class RightType(str, PyEnum):
    """Derechos del interesado según Art. 15-22 RGPD."""
    ACCESS = "access"                    # Art. 15 — Acceso
    RECTIFICATION = "rectification"      # Art. 16 — Rectificación
    ERASURE = "erasure"                  # Art. 17 — Supresión (derecho al olvido)
    RESTRICTION = "restriction"          # Art. 18 — Limitación del tratamiento
    PORTABILITY = "portability"          # Art. 20 — Portabilidad
    OBJECTION = "objection"              # Art. 21 — Oposición
    AUTOMATED_DECISION = "automated"     # Art. 22 — Decisiones automatizadas


class RequestStatus(str, PyEnum):
    """Estados del workflow de solicitud de derechos."""
    RECEIVED = "received"                        # Registrada, plazo iniciado
    IDENTITY_VERIFICATION = "identity_verification"  # Art. 12.6 — Verificando identidad
    IN_PROGRESS = "in_progress"                  # Identidad verificada, ejecutando
    RESOLVED = "resolved"                        # Solicitud ejecutada
    NOTIFIED = "notified"                        # Respuesta comunicada al interesado
    CLOSED = "closed"                            # Proceso finalizado
    EXTENDED = "extended"                        # Art. 12.3 — Plazo prorrogado (+2 meses)


class RequestResolution(str, PyEnum):
    """Resultado de la solicitud."""
    GRANTED = "granted"                  # Estimada totalmente
    PARTIALLY_GRANTED = "partially"      # Estimada parcialmente
    DENIED = "denied"                    # Denegada con motivación
    WITHDRAWN = "withdrawn"              # Retirada por el interesado


class SubjectRightsRequest(BaseModel):
    """Solicitud de ejercicio de derechos ARCO+ (Art. 15-22 RGPD).

    El plazo legal de 30 días (Art. 12.3) se computa automáticamente
    desde received_date. Prorrogable a 60 días en casos complejos.
    """
    __tablename__ = "subject_rights_requests"

    # --- Identificación ---
    code = Column(String(50), unique=True,
                  comment="Código: SRR-2026-001")
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.RECEIVED)

    # --- Derecho ejercido ---
    right_type = Column(SQLEnum(RightType), nullable=False,
                        comment="Art. 15-22 — Tipo de derecho ejercido")

    # --- Datos del solicitante ---
    requester_name = Column(String(255), nullable=False,
                            comment="Nombre del interesado")
    requester_id_type = Column(String(50),
                               comment="DNI, NIE, pasaporte")
    requester_id_number = Column(String(100),
                                 comment="Número de documento (cifrado en reposo)")
    requester_email = Column(String(255),
                             comment="Email de contacto (cifrado en reposo)")
    requester_phone = Column(String(50), nullable=True)
    is_representative = Column(Boolean, default=False,
                               comment="¿Actúa un representante?")
    representative_name = Column(String(255), nullable=True)
    representative_document = Column(String(255), nullable=True,
                                     comment="Acreditación del representante")

    # --- Canal de recepción ---
    reception_channel = Column(String(50),
                               comment="web_form, email, postal, in_person")
    reception_details = Column(Text, nullable=True,
                               comment="Referencia del canal: nº registro, email, etc.")

    # --- Fechas y plazos legales ---
    received_date = Column(DateTime, nullable=False,
                           comment="Fecha de recepción — inicia cómputo Art. 12.3")
    deadline_date = Column(DateTime, nullable=False,
                           comment="Fecha límite: received_date + 30 días")
    extended = Column(Boolean, default=False,
                      comment="¿Plazo prorrogado? (Art. 12.3 párrafo 2)")
    extension_reason = Column(Text, nullable=True,
                              comment="Motivo de la prórroga")
    extension_notified_date = Column(DateTime, nullable=True,
                                     comment="Fecha en que se notificó la prórroga")
    resolved_date = Column(DateTime, nullable=True)
    notified_date = Column(DateTime, nullable=True)

    # --- Verificación de identidad ---
    identity_verified = Column(Boolean, default=False)
    identity_verification_method = Column(String(100), nullable=True,
                                          comment="DNI electrónico, certificado digital, presencial")
    identity_verified_at = Column(DateTime, nullable=True)
    identity_verified_by = Column(BigInteger, nullable=True)

    # --- Resolución ---
    resolution = Column(SQLEnum(RequestResolution), nullable=True)
    resolution_summary = Column(Text, nullable=True,
                                comment="Resumen de la resolución")
    denial_reason = Column(Text, nullable=True,
                           comment="Motivación si se deniega (obligatoria)")

    # --- Tratamientos afectados ---
    affected_activities = Column(
        JSON, comment='IDs de tratamientos afectados por la solicitud')

    # --- Asignación ---
    assigned_to = Column(BigInteger, ForeignKey("users.id"), nullable=True,
                         comment="Responsable de gestionar la solicitud")

    # --- Campos calculados al crear ---
    @staticmethod
    def calculate_deadline(received_date: datetime,
                           extended: bool = False) -> datetime:
        """Calcula la fecha límite según Art. 12.3 RGPD.

        Plazo base: 30 días naturales desde recepción.
        Prórroga: +60 días adicionales (total 90) en casos complejos.
        """
        base_days = 30
        if extended:
            base_days = 90  # 30 + 60 días de prórroga
        return received_date + timedelta(days=base_days)
