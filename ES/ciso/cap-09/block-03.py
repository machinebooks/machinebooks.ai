# Extraído de: LibroCISO/cap-09-nis2-dora-tsunami.md
# Modelo DORA — Incidentes TIC y proveedores terceros
# Diseñado desde los Arts. 17-18 y 28-30 del Reglamento 2022/2554

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, JSON,
    BigInteger, Float, ForeignKey, Enum as SQLEnum
)
from app.models.base import BaseModel


class DORAIncidentClassification(str, PyEnum):
    """Clasificación de incidentes TIC según Art. 18 DORA."""
    MINOR = "minor"
    MAJOR = "major"          # Requiere notificación
    CRITICAL = "critical"    # Requiere notificación inmediata


class DORAICTIncident(BaseModel):
    """Incidente TIC según DORA Art. 17-23.

    DORA define criterios específicos para clasificar un incidente
    como 'grave' (Art. 18): clientes afectados, duración, alcance
    geográfico, pérdida de datos, impacto económico, criticidad
    de los servicios afectados.
    """
    __tablename__ = "dora_ict_incidents"

    incident_code = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Clasificación según criterios Art. 18
    classification = Column(
        SQLEnum(DORAIncidentClassification), nullable=False
    )

    # Criterios de clasificación (Art. 18.1)
    affected_clients_count = Column(
        BigInteger, nullable=True,
        comment="Art. 18.1.a: Número de clientes afectados"
    )
    duration_hours = Column(
        Float, nullable=True,
        comment="Art. 18.1.b: Duración del incidente en horas"
    )
    geographical_spread = Column(
        JSON, nullable=True,
        comment="Art. 18.1.c: Alcance geográfico (países, regiones)"
    )
    data_losses = Column(
        Boolean, default=False,
        comment="Art. 18.1.d: ¿Pérdida de datos?"
    )
    data_integrity_impact = Column(
        Boolean, default=False,
        comment="Art. 18.1.d: ¿Impacto en integridad de datos?"
    )
    economic_impact = Column(
        Float, nullable=True,
        comment="Art. 18.1.e: Impacto económico estimado (EUR)"
    )
    critical_services_affected = Column(
        JSON, nullable=True,
        comment="Art. 18.1.f: Servicios críticos afectados"
    )

    # Temporalidad
    detected_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Causa y mitigación
    root_cause = Column(Text, nullable=True)
    recovery_actions = Column(JSON, nullable=True)

    # Vinculación con NIS2 (si aplica)
    linked_nis2_incident_id = Column(
        BigInteger, ForeignKey("nis2_incidents.id"), nullable=True,
        comment="Si la entidad está sujeta a NIS2 y DORA simultáneamente"
    )


class DORAICTProvider(BaseModel):
    """Proveedor tercero de servicios TIC según DORA Art. 28-30.

    DORA exige un registro de todos los acuerdos contractuales
    con proveedores TIC, evaluación de riesgo de concentración
    y planes de salida para proveedores críticos.
    """
    __tablename__ = "dora_ict_providers"

    # Identificación del proveedor
    provider_name = Column(String(300), nullable=False)
    provider_identifier = Column(
        String(100), nullable=True,
        comment="LEI o identificador único del proveedor"
    )

    # Servicios y criticidad
    services_provided = Column(
        JSON, nullable=False,
        comment="Lista de servicios TIC prestados"
    )
    supports_critical_functions = Column(
        Boolean, default=False,
        comment="Art. 28.1: ¿Soporta funciones críticas o importantes?"
    )
    operational_functions = Column(
        JSON, nullable=True,
        comment="Funciones operativas soportadas"
    )

    # Ubicación y jurisdicción (Art. 28.7)
    data_processing_location = Column(
        JSON, nullable=True,
        comment="Ubicaciones donde se procesan/almacenan datos"
    )
    provider_jurisdiction = Column(
        String(100), nullable=True,
        comment="Jurisdicción del proveedor"
    )

    # Evaluación de riesgo
    risk_assessment_date = Column(DateTime(timezone=True), nullable=True)
    risk_level = Column(
        String(20), nullable=True,
        comment="low, medium, high, critical"
    )
    concentration_risk = Column(
        Boolean, default=False,
        comment="Art. 29: ¿Riesgo de concentración identificado?"
    )

    # Contractual
    contract_start_date = Column(DateTime(timezone=True), nullable=True)
    contract_end_date = Column(DateTime(timezone=True), nullable=True)
    exit_plan_exists = Column(
        Boolean, default=False,
        comment="Art. 28.8: ¿Existe plan de salida documentado?"
    )
    exit_plan_last_tested = Column(
        DateTime(timezone=True), nullable=True,
        comment="Última vez que se probó el plan de salida"
    )

    # Subcontratación (Art. 29.2)
    subcontracting_chain = Column(
        JSON, nullable=True,
        comment="Cadena de subcontratación del proveedor"
    )
