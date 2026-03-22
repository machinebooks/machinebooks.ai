# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: modelos/ai_governance.py
# Inventario de sistemas de IA conforme al AI Act (Reglamento 2024/1689)

from enum import Enum
from sqlalchemy import Column, String, Text, Enum as SQLEnum, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel  # BaseModel con audit trail, soft delete, tenant_id


class AIRiskLevel(str, Enum):
    """Clasificación de riesgo según AI Act Art. 5 y Anexo III."""
    UNACCEPTABLE = "unacceptable"   # Art. 5 — prohibido
    HIGH = "high"                    # Anexo III — evaluación de conformidad obligatoria
    LIMITED = "limited"              # Transparencia obligatoria
    MINIMAL = "minimal"              # Sin obligaciones específicas
    GPAI = "gpai"                    # Modelo de propósito general (obligaciones específicas)
    GPAI_SYSTEMIC = "gpai_systemic"  # GPAI con riesgo sistémico (>10²⁵ FLOPS)


class AISupervisionLevel(str, Enum):
    """Niveles de supervisión humana según AI Act Art. 14."""
    HUMAN_IN_THE_LOOP = "hitl"      # Aprobación humana antes de cada acción
    HUMAN_ON_THE_LOOP = "hotl"      # Supervisión durante operación
    HUMAN_IN_COMMAND = "hic"        # Capacidad de intervención y parada


class AnnexIIICategory(str, Enum):
    """Categorías de alto riesgo del Anexo III del AI Act."""
    BIOMETRIC = "biometric"                     # Cat 1: Identificación biométrica
    CRITICAL_INFRASTRUCTURE = "critical_infra"  # Cat 2: Infraestructura crítica
    EDUCATION = "education"                     # Cat 3: Educación y formación
    EMPLOYMENT = "employment"                   # Cat 4: Empleo y gestión de trabajadores
    ESSENTIAL_SERVICES = "essential_services"    # Cat 5: Servicios esenciales
    LAW_ENFORCEMENT = "law_enforcement"          # Cat 6: Aplicación de la ley
    MIGRATION = "migration"                     # Cat 7: Migración y fronteras
    JUSTICE = "justice"                          # Cat 8: Administración de justicia


class AIGovernanceRecord(BaseModel):
    """Registro de un sistema de IA en el inventario de gobernanza.

    Cada registro representa un sistema de IA desplegado o en desarrollo,
    con toda la información necesaria para clasificación y seguimiento
    conforme al AI Act.
    """
    __tablename__ = "ai_governance_records"

    name = Column(String(200), nullable=False)            # Nombre del sistema
    description = Column(Text, nullable=False)             # Descripción funcional
    purpose = Column(Text, nullable=False)                 # Finalidad específica
    provider = Column(String(200))                         # Proveedor del modelo/sistema
    model_name = Column(String(200))                       # Nombre del modelo (ej: claude-sonnet-4-6)
    model_version = Column(String(50))                     # Versión específica

    # Clasificación de riesgo
    risk_level = Column(SQLEnum(AIRiskLevel), nullable=False)
    risk_level_auto = Column(SQLEnum(AIRiskLevel))         # Clasificación automática propuesta
    risk_justification = Column(Text)                      # Justificación si difiere de la automática
    annex_iii_category = Column(SQLEnum(AnnexIIICategory)) # Categoría si es alto riesgo

    # Contexto de uso
    sector = Column(String(100))                           # Sector de aplicación
    affected_persons = Column(Text)                        # Personas afectadas por el sistema
    data_categories = Column(JSON)                         # Categorías de datos que procesa
    deployment_type = Column(String(50))                   # cloud, on-premise, hybrid

    # Supervisión humana
    supervision_level = Column(SQLEnum(AISupervisionLevel), nullable=False)
    supervisor_role = Column(String(100))                  # Rol responsable de supervisión

    # Estado
    status = Column(String(50), default="active")          # active, suspended, decommissioned
    discovery_source = Column(String(50))                  # auto, manual, import

    # Relaciones
    conformity_assessments = relationship("ConformityAssessment", back_populates="ai_record")
    monitoring_metrics = relationship("AIMonitoringMetric", back_populates="ai_record")
    governance_controls = relationship("AIGovernanceControl", back_populates="ai_record")
    governance_incidents = relationship("AIGovernanceIncident", back_populates="ai_record")
