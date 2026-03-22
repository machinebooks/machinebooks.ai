# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
from sqlalchemy import BigInteger, Boolean, Date, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import DATETIME, JSON
from sqlalchemy.orm import Mapped, mapped_column
from models.base import BaseModel
import enum


class SourceType(str, enum.Enum):
    """Tipo de fuente normativa monitorizada."""
    OFFICIAL_JOURNAL = "official_journal"   # BOE, DOUE
    REGULATOR = "regulator"                 # AEPD, CNMC
    STANDARDS_BODY = "standards_body"       # ISO, CEN/CENELEC
    SECTOR_AUTHORITY = "sector_authority"   # CCN-CERT, ENISA


class CheckFrequency(str, enum.Enum):
    """Frecuencia de consulta a la fuente."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class UpdateStatus(str, enum.Enum):
    """Máquina de estados para actualizaciones detectadas."""
    NEW = "new"                    # Detectada, pendiente de análisis
    ANALYZING = "analyzing"        # Análisis en curso (humano o IA)
    ANALYZED = "analyzed"          # Analizada, pendiente de decisión
    DISMISSED = "dismissed"        # Sin impacto relevante
    REQUIRES_ACTION = "requires_action"  # Requiere modificar controles


class RegulatorySource(BaseModel):
    """Fuente de normativa monitorizada.

    Cada fuente representa un organismo o diario oficial
    que publica regulación relevante para la organización.
    """
    __tablename__ = "regulatory_sources"

    name: Mapped[str] = mapped_column(
        String(200), nullable=False,
        comment="Nombre: BOE, DOUE, AEPD, ENISA, CCN-CERT"
    )
    source_type: Mapped[str] = mapped_column(
        Enum(SourceType), nullable=False,
        default=SourceType.OFFICIAL_JOURNAL
    )
    url: Mapped[str | None] = mapped_column(
        String(1000), nullable=True,
        comment="URL base a monitorizar"
    )
    country: Mapped[str | None] = mapped_column(
        String(10), nullable=True,
        comment="País ISO: ES, EU, etc."
    )
    check_frequency: Mapped[str] = mapped_column(
        Enum(CheckFrequency), nullable=False,
        default=CheckFrequency.DAILY
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DATETIME(fsp=6), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
