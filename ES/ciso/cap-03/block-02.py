# Extraído de: LibroCISO/cap-03-ecosistema-tecnico.md
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from uuid import uuid4


class BaseModel(DeclarativeBase):
    """Base para todos los modelos GRC.
    Garantiza multi-tenancy, auditoría completa y soft delete
    en los 90+ modelos del sistema."""

    __abstract__ = True

    # Identificación
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(
        String(36), unique=True, nullable=False,
        default=lambda: str(uuid4())
        # UUID público para APIs — el id numérico nunca se expone
    )

    # Multi-tenancy obligatorio
    corporate_id = Column(
        Integer, nullable=False, index=True
        # TODA query filtra por corporate_id.
        # Un usuario del tenant A nunca ve datos del tenant B.
        # Si este campo falta, el modelo es un agujero de seguridad.
    )

    # Auditoría — quién hizo qué y cuándo
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(Integer, nullable=True)

    # Soft delete — nunca se borra físicamente un registro GRC
    # En compliance, borrar evidencia es peor que el incumplimiento original
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)

    # Versionado optimista — previene escrituras concurrentes
    # Si dos usuarios editan el mismo riesgo, el segundo recibe un 409 Conflict
    version = Column(Integer, default=1, nullable=False)

    # Extensibilidad — campos adicionales sin migración de esquema
    # Útil para personalizaciones por tenant sin alterar la estructura base
    extra_data = Column(JSON, nullable=True)
