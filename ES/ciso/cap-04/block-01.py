# Extraído de: LibroCISO/cap-04-registro-tratamientos.md
# Schema Pydantic para creación de tratamiento
# Valida que los campos obligatorios del Art. 30 estén presentes

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class LegalBasisEnum(str, Enum):
    consent = "consent"
    contract = "contract"
    legal_obligation = "legal_obligation"
    vital_interest = "vital_interest"
    public_interest = "public_interest"
    legitimate_interest = "legitimate_interest"


class ProcessingActivityCreate(BaseModel):
    """Schema de creación — los campos obligatorios del Art. 30 son required."""

    # Obligatorios
    name: str = Field(..., min_length=3, max_length=255,
                      description="Nombre descriptivo del tratamiento")
    controller_name: str = Field(..., min_length=3,
                                description="Art. 30.1.a — Responsable")
    purposes: list[str] = Field(..., min_length=1,
                                description="Art. 30.1.b — Al menos una finalidad")
    legal_basis: LegalBasisEnum = Field(...,
                                       description="Art. 6.1 — Base jurídica")

    # Recomendados (obligatorios al activar)
    description: Optional[str] = None
    controller_contact: Optional[str] = None
    dpo_name: Optional[str] = None
    dpo_contact: Optional[str] = None
    data_subject_categories: Optional[list[str]] = None
    personal_data_categories: Optional[list[str]] = None
    special_categories: bool = False
    special_categories_detail: Optional[list[str]] = None
    recipients: Optional[list[str]] = None
    international_transfers: bool = False
    transfer_countries: Optional[list[str]] = None
    transfer_safeguards: Optional[str] = None
    retention_period: Optional[str] = None
    retention_criteria: Optional[str] = None
    security_measures: Optional[list[str]] = None
    risk_level: Optional[str] = None

    @field_validator("special_categories_detail")
    @classmethod
    def validate_special_categories(cls, v, info):
        """Si se activan categorías especiales, debe indicarse cuáles."""
        if info.data.get("special_categories") and not v:
            raise ValueError(
                "Si special_categories=True, debe indicar cuáles "
                "(Art. 9 RGPD): salud, biométricos, genéticos, etc."
            )
        return v

    @field_validator("transfer_countries")
    @classmethod
    def validate_transfers(cls, v, info):
        """Si hay transferencias internacionales, debe indicarse destino."""
        if info.data.get("international_transfers") and not v:
            raise ValueError(
                "Si international_transfers=True, debe indicar "
                "los países destino (Art. 30.1.e RGPD)"
            )
        return v


class ProcessingActivityActivate(ProcessingActivityCreate):
    """Schema para activar un tratamiento — validación completa Art. 30."""

    # Al activar, estos campos pasan a ser obligatorios
    data_subject_categories: list[str] = Field(
        ..., min_length=1,
        description="Art. 30.1.c — Categorías de interesados")
    personal_data_categories: list[str] = Field(
        ..., min_length=1,
        description="Art. 30.1.c — Categorías de datos personales")
    retention_period: str = Field(
        ..., min_length=1,
        description="Art. 30.1.f — Plazo de conservación")
    security_measures: list[str] = Field(
        ..., min_length=1,
        description="Art. 30.1.g — Medidas de seguridad Art. 32")
