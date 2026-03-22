# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: models/audit.py

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Index
)
from app.models.base import BaseModel


class AuditTrail(BaseModel):
    """Registro de auditoría para operaciones mutantes.

    Índices optimizados para las consultas más frecuentes:
    - DPO busca por corporate_id + recurso + rango de fechas
    - Admin busca por user_id + rango de fechas
    - SOC busca por IP + status_code + rango de fechas
    """
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    corporate_id = Column(String(50), nullable=False, index=True)
    action = Column(String(10), nullable=False)     # POST, PUT, PATCH, DELETE
    resource = Column(String(500), nullable=False)   # /api/treatments/123
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(36), nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        # Índice compuesto para búsquedas del DPO
        Index(
            "ix_audit_tenant_resource_ts",
            "corporate_id", "resource", "timestamp"
        ),
        # Índice compuesto para búsquedas del SOC
        Index(
            "ix_audit_ip_status_ts",
            "ip_address", "status_code", "timestamp"
        ),
    )
