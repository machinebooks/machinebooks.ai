# Extraído de: LibroCISO/cap-09-nis2-dora-tsunami.md
# Modelo BCM — Continuidad de negocio (ISO 22301)
# BIA + Planes de recuperación vinculados a NIS2 Art. 21 y DORA Art. 11

from sqlalchemy import (
    Column, String, Text, DateTime, Integer,
    Float, JSON, BigInteger, ForeignKey, Enum as SQLEnum
)
from app.models.base import BaseModel


class BCMCriticality(str, PyEnum):
    """Criticidad del proceso de negocio."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BusinessImpactAnalysis(BaseModel):
    """Análisis de Impacto en el Negocio (BIA) por proceso.

    El BIA es el núcleo de ISO 22301: determina para cada proceso
    cuánto tiempo puede estar interrumpido (MTPD), en cuánto tiempo
    hay que recuperarlo (RTO) y cuánta pérdida de datos es tolerable (RPO).
    """
    __tablename__ = "bcm_bia"

    # Proceso de negocio
    process_name = Column(String(300), nullable=False)
    process_description = Column(Text, nullable=True)
    process_owner = Column(
        String(200), nullable=True,
        comment="Responsable funcional del proceso"
    )
    department = Column(String(200), nullable=True)

    # Criticidad
    criticality = Column(
        SQLEnum(BCMCriticality), nullable=False,
        comment="Criticidad del proceso para la organización"
    )

    # Parámetros de recuperación (núcleo del BIA)
    mtpd_hours = Column(
        Float, nullable=False,
        comment="Maximum Tolerable Period of Disruption (horas). "
                "Tiempo máximo antes de consecuencias inaceptables."
    )
    rto_hours = Column(
        Float, nullable=False,
        comment="Recovery Time Objective (horas). "
                "Tiempo objetivo para restaurar el proceso. "
                "Siempre debe ser <= MTPD."
    )
    rpo_hours = Column(
        Float, nullable=False,
        comment="Recovery Point Objective (horas). "
                "Antigüedad máxima de datos perdidos tolerable."
    )

    # Impacto por tipo (qué pasa si el proceso se interrumpe)
    financial_impact = Column(
        Float, nullable=True,
        comment="Impacto financiero estimado por hora de interrupción (EUR)"
    )
    reputational_impact = Column(
        String(20), nullable=True,
        comment="low, medium, high, critical"
    )
    regulatory_impact = Column(
        String(20), nullable=True,
        comment="Impacto regulatorio: ¿incumplimiento por interrupción?"
    )
    operational_impact = Column(Text, nullable=True)

    # Dependencias
    depends_on_processes = Column(
        JSON, nullable=True,
        comment="Otros procesos de los que depende"
    )
    depends_on_systems = Column(
        JSON, nullable=True,
        comment="Sistemas TIC de los que depende"
    )
    depends_on_providers = Column(
        JSON, nullable=True,
        comment="Proveedores externos de los que depende"
    )

    # Recursos mínimos para operación degradada
    minimum_staff = Column(Integer, nullable=True)
    minimum_systems = Column(JSON, nullable=True)

    # Vinculación con otros módulos
    linked_asset_ids = Column(
        JSON, nullable=True,
        comment="Activos del módulo de riesgo vinculados"
    )

    # Fecha de última revisión
    last_review_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)


class RecoveryPlan(BaseModel):
    """Plan de recuperación vinculado a un proceso del BIA.

    Documenta los pasos para restaurar el proceso dentro del RTO.
    No ejecuta la recuperación — documenta, versiona y verifica.
    """
    __tablename__ = "bcm_recovery_plans"

    bia_id = Column(
        BigInteger, ForeignKey("bcm_bia.id"), nullable=False
    )

    plan_name = Column(String(300), nullable=False)
    plan_version = Column(String(20), nullable=False, default="1.0")

    # Contenido del plan
    activation_criteria = Column(
        Text, nullable=False,
        comment="Criterios para activar este plan"
    )
    recovery_steps = Column(
        JSON, nullable=False,
        comment="Pasos de recuperación ordenados"
    )
    responsible_team = Column(
        JSON, nullable=True,
        comment="Equipo responsable de ejecutar el plan"
    )
    communication_plan = Column(
        Text, nullable=True,
        comment="Protocolo de comunicación durante la crisis"
    )

    # Testing del plan
    last_test_date = Column(DateTime(timezone=True), nullable=True)
    last_test_result = Column(
        String(20), nullable=True,
        comment="passed, partial, failed"
    )
    next_test_date = Column(DateTime(timezone=True), nullable=True)

    # Estado
    status = Column(
        String(20), nullable=False, default="draft",
        comment="draft, approved, active, archived"
    )
    approved_by = Column(String(200), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
