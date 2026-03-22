# Extraído de: LibroCISO/cap-06-brechas-encargados-transferencias.md
# Modelo de Brecha de Seguridad — diseñado desde Art. 33-34 RGPD
# Máquina de estados con reloj automático de 72 horas

from enum import Enum as PyEnum
from datetime import datetime, timedelta
from sqlalchemy import (
    Column, String, Text, Boolean, BigInteger, Integer,
    ForeignKey, DateTime, JSON, Enum as SQLEnum
)
from app.models.base import BaseModel  # multi-tenant, audit, soft delete


class BreachStatus(str, PyEnum):
    """Ciclo de vida de una brecha — transiciones controladas."""
    DETECTED = "detected"               # Registro inicial
    INVESTIGATING = "investigating"     # Investigación en curso
    ASSESSED = "assessed"               # Evaluada: se decide si notificar
    NOTIFIED_AUTHORITY = "notified_authority"   # Art. 33 — Notificada a AEPD
    NOTIFIED_SUBJECTS = "notified_subjects"    # Art. 34 — Notificada a interesados
    CLOSED = "closed"                   # Resuelta y documentada


class BreachSeverity(str, PyEnum):
    """Severidad basada en criterios AEPD."""
    LOW = "low"           # Sin riesgo apreciable
    MEDIUM = "medium"     # Riesgo bajo-medio
    HIGH = "high"         # Riesgo alto — notificación AEPD probable
    CRITICAL = "critical" # Riesgo muy alto — notificación AEPD + interesados


class BreachType(str, PyEnum):
    """Clasificación según tipo de impacto en los datos."""
    CONFIDENTIALITY = "confidentiality"   # Acceso no autorizado
    INTEGRITY = "integrity"               # Alteración no autorizada
    AVAILABILITY = "availability"         # Pérdida de acceso
    MIXED = "mixed"                       # Combinación de tipos


# Transiciones válidas: impide saltos ilegales en el ciclo de vida
VALID_TRANSITIONS = {
    BreachStatus.DETECTED: [BreachStatus.INVESTIGATING],
    BreachStatus.INVESTIGATING: [BreachStatus.ASSESSED],
    BreachStatus.ASSESSED: [
        BreachStatus.NOTIFIED_AUTHORITY,  # Si hay riesgo
        BreachStatus.CLOSED,              # Si no hay riesgo: cierre directo
    ],
    BreachStatus.NOTIFIED_AUTHORITY: [
        BreachStatus.NOTIFIED_SUBJECTS,   # Si riesgo alto: notificar interesados
        BreachStatus.CLOSED,              # Si riesgo no alto: cierre tras AEPD
    ],
    BreachStatus.NOTIFIED_SUBJECTS: [BreachStatus.CLOSED],
    BreachStatus.CLOSED: [],  # Estado terminal
}


class DataBreach(BaseModel):
    """Brecha de datos personales (Art. 33-34 RGPD).

    El campo notification_deadline se calcula automáticamente
    como detected_at + 72 horas. No es editable manualmente.
    Hereda del BaseModel común (Capítulo 3): multi-tenant, audit, soft delete.
    """
    __tablename__ = "data_breaches"

    # --- Identificación ---
    code = Column(String(50), unique=True, nullable=False,
                  comment="Código: BREACH-2025-001")
    title = Column(String(500), nullable=False,
                   comment="Descripción corta de la brecha")
    description = Column(Text, nullable=False,
                         comment="Descripción detallada del incidente")

    # --- Clasificación ---
    breach_type = Column(SQLEnum(BreachType), nullable=False,
                         comment="Confidencialidad, integridad, disponibilidad")
    severity = Column(SQLEnum(BreachSeverity), nullable=False,
                      comment="Severidad evaluada según criterios AEPD")
    status = Column(SQLEnum(BreachStatus), default=BreachStatus.DETECTED,
                    comment="Estado actual en la máquina de estados")

    # --- Temporalidad (Art. 33.1 — 72 horas) ---
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                         comment="Momento de detección/conocimiento")
    notification_deadline = Column(
        DateTime, nullable=False,
        comment="detected_at + 72h — calculado automáticamente")
    notified_authority_at = Column(
        DateTime, nullable=True,
        comment="Timestamp real de notificación a AEPD")
    notified_subjects_at = Column(
        DateTime, nullable=True,
        comment="Timestamp de comunicación a interesados")
    closed_at = Column(DateTime, nullable=True)

    # --- Impacto (Art. 33.3) ---
    affected_count = Column(Integer, nullable=True,
                            comment="Número estimado de interesados afectados")
    data_categories_affected = Column(
        JSON, comment='["identificativos", "financieros", "salud"]')
    special_categories_affected = Column(
        Boolean, default=False,
        comment="¿Afecta a datos del Art. 9?")

    # --- Respuesta ---
    root_cause = Column(Text, comment="Causa raíz identificada")
    measures_taken = Column(JSON,
                            comment='Medidas adoptadas para mitigar')
    measures_proposed = Column(JSON,
                               comment='Medidas propuestas para evitar recurrencia')

    # --- Notificación AEPD ---
    authority_reference = Column(
        String(100), nullable=True,
        comment="Número de expediente AEPD, si procede")
    notify_subjects_required = Column(
        Boolean, default=False,
        comment="Art. 34 — ¿Requiere comunicación a interesados?")

    # --- Responsables ---
    reported_by = Column(BigInteger, ForeignKey("users.id"),
                         comment="Quién detectó/reportó la brecha")
    dpo_id = Column(BigInteger, ForeignKey("users.id"),
                    comment="DPO asignado a la gestión")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Reloj de 72 horas automático
        if self.detected_at and not self.notification_deadline:
            self.notification_deadline = self.detected_at + timedelta(hours=72)

    def can_transition_to(self, new_status: BreachStatus) -> bool:
        """Verifica si la transición de estado es válida."""
        return new_status in VALID_TRANSITIONS.get(self.status, [])

    @property
    def hours_remaining(self) -> float:
        """Horas restantes hasta el deadline de notificación."""
        if self.notified_authority_at:
            return 0  # Ya notificada
        delta = self.notification_deadline - datetime.utcnow()
        return max(0, delta.total_seconds() / 3600)

    @property
    def is_overdue(self) -> bool:
        """True si se ha superado el plazo de 72h sin notificar."""
        if self.notified_authority_at:
            return False
        return datetime.utcnow() > self.notification_deadline
