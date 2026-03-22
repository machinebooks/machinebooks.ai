# Extraído de: LibroCISO/cap-09-nis2-dora-tsunami.md
# Modelo de notificación NIS2 — tres fases con plazos legales
# Diseñado desde el Art. 23 de la Directiva 2022/2555

from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, JSON,
    BigInteger, ForeignKey, Enum as SQLEnum
)
from app.models.base import BaseModel


class NIS2IncidentSeverity(str, PyEnum):
    """Gravedad del incidente según criterios NIS2."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NIS2NotificationPhase(str, PyEnum):
    """Fases de notificación Art. 23 NIS2."""
    EARLY_WARNING = "early_warning"     # 24 horas
    FORMAL_NOTIFICATION = "formal"      # 72 horas
    FINAL_REPORT = "final_report"       # 1 mes


class NIS2Incident(BaseModel):
    """Incidente significativo según NIS2.

    Un incidente es significativo si causa o puede causar:
    - Perturbación operativa grave del servicio
    - Pérdidas financieras para la entidad afectada
    - Perjuicios a personas físicas o jurídicas por daños
      materiales, físicos o inmateriales
    """
    __tablename__ = "nis2_incidents"

    # Identificación del incidente
    incident_code = Column(
        String(50), unique=True, nullable=False,
        comment="Código único: NIS2-YYYYMMDD-NNNN"
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Clasificación
    severity = Column(
        SQLEnum(NIS2IncidentSeverity), nullable=False,
        comment="Gravedad según criterios NIS2 Art. 23"
    )
    is_significant = Column(
        Boolean, default=True,
        comment="¿Incidente significativo? Solo los significativos "
                "requieren notificación"
    )
    is_malicious = Column(
        Boolean, nullable=True,
        comment="Art. 23.4.a: ¿sospecha de acto ilícito o malicioso?"
    )
    is_cross_border = Column(
        Boolean, default=False,
        comment="Art. 23.4.a: ¿impacto transfronterizo?"
    )

    # Temporalidad del incidente
    detected_at = Column(
        DateTime(timezone=True), nullable=False,
        comment="Momento de detección del incidente"
    )
    awareness_at = Column(
        DateTime(timezone=True), nullable=False,
        comment="Momento en que la entidad tuvo conocimiento. "
                "Los plazos cuentan desde aquí."
    )
    resolved_at = Column(
        DateTime(timezone=True), nullable=True,
        comment="Momento de resolución. NULL = incidente activo"
    )

    # Plazos de notificación (calculados desde awareness_at)
    early_warning_deadline = Column(
        DateTime(timezone=True), nullable=False,
        comment="Plazo alerta temprana: awareness_at + 24h"
    )
    formal_notification_deadline = Column(
        DateTime(timezone=True), nullable=False,
        comment="Plazo notificación formal: awareness_at + 72h"
    )
    final_report_deadline = Column(
        DateTime(timezone=True), nullable=False,
        comment="Plazo informe final: awareness_at + 30 días"
    )

    # Impacto
    affected_services = Column(
        JSON, nullable=True,
        comment="Servicios esenciales/importantes afectados"
    )
    affected_users_count = Column(
        BigInteger, nullable=True,
        comment="Número estimado de usuarios afectados"
    )
    affected_countries = Column(
        JSON, nullable=True,
        comment="Países afectados si es transfronterizo"
    )

    # Causa raíz y mitigación (para informe final)
    root_cause = Column(Text, nullable=True)
    mitigation_measures = Column(JSON, nullable=True)
    ioc_indicators = Column(
        JSON, nullable=True,
        comment="Indicadores de compromiso (IoC)"
    )

    # Vinculación con incidentes RGPD (si hay datos personales)
    linked_breach_id = Column(
        BigInteger, ForeignKey("data_breaches.id"), nullable=True,
        comment="Si el incidente implica datos personales, "
                "vinculación con brecha RGPD Art. 33"
    )


class NIS2Notification(BaseModel):
    """Notificación de una fase específica al CSIRT/autoridad.

    Cada incidente genera hasta 3 notificaciones (una por fase).
    El sistema crea las tres automáticamente al registrar el incidente.
    """
    __tablename__ = "nis2_notifications"

    incident_id = Column(
        BigInteger, ForeignKey("nis2_incidents.id"), nullable=False
    )
    phase = Column(
        SQLEnum(NIS2NotificationPhase), nullable=False,
        comment="Fase de notificación"
    )
    deadline = Column(
        DateTime(timezone=True), nullable=False,
        comment="Fecha límite para esta fase"
    )

    # Estado
    status = Column(
        String(20), nullable=False, default="pending",
        comment="pending, completed, overdue"
    )
    completed_at = Column(
        DateTime(timezone=True), nullable=True,
        comment="Momento en que se completó la notificación"
    )

    # Contenido de la notificación
    content = Column(Text, nullable=True)
    submitted_to = Column(
        String(200), nullable=True,
        comment="CSIRT nacional o autoridad competente"
    )
    submission_reference = Column(
        String(100), nullable=True,
        comment="Referencia de la autoridad receptora"
    )
