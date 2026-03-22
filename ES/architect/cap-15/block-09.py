# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Enum as SAEnum
from datetime import datetime
from database import Base

class NotificationType(str, Enum):
    NEW_OPPORTUNITY = "NEW_OPPORTUNITY"   # Nueva oportunidad relevante
    DEAL_STALLED = "DEAL_STALLED"         # Propuesta sin movimiento >30 días
    ACCOUNT_RISK = "ACCOUNT_RISK"         # Señal de riesgo en cuenta cliente
    REPORT_READY = "REPORT_READY"         # Informe o análisis completado
    OPPORTUNITY_MATCH = "OPPORTUNITY_MATCH"  # Match automático oportunidad/portfolio
    SYSTEM = "SYSTEM"                     # Notificación de sistema (mantenimiento, errores)

class NotificationPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    type = Column(SAEnum(NotificationType), nullable=False)
    priority = Column(SAEnum(NotificationPriority), default=NotificationPriority.MEDIUM)

    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)

    # Deep linking: URL directa al recurso relacionado
    action_url = Column(String(500), nullable=True)

    # Contexto rico: datos específicos del tipo de notificación
    extra_data = Column(JSON, nullable=True)

    # Estado
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
