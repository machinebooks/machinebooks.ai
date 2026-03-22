# Extraído de: LibroConsultor/cap-13-gap-analysis.md
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


class MaturityLevel(IntEnum):
    """Niveles de madurez para evaluación de controles."""
    INEXISTENTE = 0   # No hay evidencia de implementación
    INICIAL = 1       # Existe de forma ad-hoc, sin formalizar
    DEFINIDO = 2      # Documentado y aprobado formalmente
    GESTIONADO = 3    # Implementado, medido y revisado
    OPTIMIZADO = 4    # Mejora continua con métricas


@dataclass
class Control:
    """Un control dentro de un framework normativo."""
    framework: str          # "ISO27001", "ENS", "NIS2", "AI_ACT"
    control_id: str         # "A.8.1", "org.1", "Art.21.2.a"
    title: str
    description: str
    category: str           # Agrupación temática
    # Controles equivalentes en otros frameworks
    cross_references: list[str] = field(default_factory=list)


@dataclass
class EvaluationCriteria:
    """Criterios de evaluación para un control, por perfil."""
    control_id: str
    org_profile: str        # "financiero_grande", "pyme_servicios"
    # Qué se espera en cada nivel de madurez
    level_criteria: dict[MaturityLevel, str] = field(
        default_factory=dict
    )


@dataclass
class GapFinding:
    """Resultado de evaluar un control contra evidencias."""
    control: Control
    current_level: MaturityLevel
    target_level: MaturityLevel
    evidence_summary: str   # Evidencias encontradas
    gap_description: str    # Qué falta para alcanzar el objetivo
    remediation: str        # Acciones recomendadas
    effort_days: float      # Estimación de esfuerzo en días
    priority: str           # "critica", "alta", "media", "baja"
    confidence: float       # 0.0-1.0, confianza en la evaluación
    affected_frameworks: list[str] = field(
        default_factory=list
    )
