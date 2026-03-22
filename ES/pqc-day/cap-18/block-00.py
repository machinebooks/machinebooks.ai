# Extraído de: LibroPQC/cap-18-roadmap.md
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional


class ShelfLife(IntEnum):
    """Cuánto tiempo deben permanecer protegidos los datos"""
    DAYS = 1        # Tokens de sesión, datos efímeros
    MONTHS = 2      # Comunicaciones operativas
    YEARS = 3       # Contratos, propiedad intelectual
    DECADES = 4     # Datos sanitarios, financieros
    PERMANENT = 5   # Secretos de estado, defensa


class Exposure(IntEnum):
    """Grado de exposición del sistema a interceptación"""
    INTERNAL_ONLY = 1     # Red aislada, sin acceso externo
    VPN_PROTECTED = 2     # Acceso externo vía VPN corporativa
    AUTHENTICATED = 3     # API pública con autenticación
    PUBLIC_FACING = 4     # Servicio público con datos sensibles
    BROADCAST = 5         # Datos transmitidos sin control de canal


class Severity(IntEnum):
    """Impacto de la rotura del algoritmo"""
    INFORMATIONAL = 1  # Metadata, datos no sensibles
    LOW = 2            # Datos internos de baja sensibilidad
    MEDIUM = 3         # Datos operativos, PII básicos
    HIGH = 4           # Datos financieros, PII sensibles
    CRITICAL = 5       # Infraestructura crítica, salud, defensa


class MigrationComplexity(IntEnum):
    """Esfuerzo necesario para migrar"""
    TRIVIAL = 1       # Cambiar configuración, sin código
    LOW = 2           # Cambiar biblioteca, tests unitarios
    MEDIUM = 3        # Refactorizar servicio, coordinar equipo
    HIGH = 4          # Cambiar protocolo, negociar con terceros
    EXTREME = 5       # Rediseño arquitectónico, múltiples sistemas


@dataclass
class PriorityScore:
    """Resultado del cálculo de prioridad"""
    shelf_life: int
    exposure: int
    severity: int
    migration_complexity: int
    composite_score: float
    priority_label: str
    recommended_timeline: str

    @property
    def risk_score(self) -> float:
        """Score de riesgo sin considerar complejidad de migración"""
        return self.shelf_life * self.exposure * self.severity

    @property
    def urgency_ratio(self) -> float:
        """Ratio riesgo / complejidad — cuanto mayor, más urgente"""
        if self.migration_complexity == 0:
            return float('inf')
        return self.risk_score / self.migration_complexity


def calculate_priority(
    shelf_life: int,
    exposure: int,
    severity: int,
    migration_complexity: int
) -> PriorityScore:
    """
    Calcula la prioridad de migración según el framework Europol.

    El score compuesto pondera riesgo (shelf_life × exposure × severity)
    contra esfuerzo (migration_complexity). Los hallazgos con alto riesgo
    y baja complejidad se migran primero — son las "victorias rápidas".
    Los hallazgos con alto riesgo y alta complejidad se planifican a
    medio plazo. Los de bajo riesgo se aceptan o se programan a largo plazo.
    """
    # Score de riesgo bruto (1 a 125)
    risk = shelf_life * exposure * severity

    # Score compuesto: riesgo ponderado por complejidad inversa
    # Complejidad alta reduce la urgencia, no el riesgo
    composite = risk * (6 - migration_complexity) / 5

    # Clasificación por umbrales
    if composite >= 50:
        label = "critical"
        timeline = "Inmediato — próximas 2 semanas"
    elif composite >= 25:
        label = "high"
        timeline = "Corto plazo — próximo trimestre"
    elif composite >= 10:
        label = "medium"
        timeline = "Medio plazo — próximos 6 meses"
    else:
        label = "low"
        timeline = "Largo plazo — próximo año"

    return PriorityScore(
        shelf_life=shelf_life,
        exposure=exposure,
        severity=severity,
        migration_complexity=migration_complexity,
        composite_score=round(composite, 2),
        priority_label=label,
        recommended_timeline=timeline
    )


def prioritize_findings(findings: List[dict]) -> List[dict]:
    """
    Ordena una lista de hallazgos por prioridad de migración.

    Cada finding debe incluir los campos: shelf_life, exposure,
    severity, migration_complexity. Si faltan, se asignan valores
    por defecto conservadores (asumiendo el peor caso).
    """
    scored = []
    for finding in findings:
        score = calculate_priority(
            shelf_life=finding.get('shelf_life', 3),
            exposure=finding.get('exposure', 3),
            severity=finding.get('severity_score', 3),
            migration_complexity=finding.get('migration_complexity', 3)
        )
        finding['priority_score'] = score.composite_score
        finding['priority_label'] = score.priority_label
        finding['recommended_timeline'] = score.recommended_timeline
        finding['urgency_ratio'] = score.urgency_ratio
        scored.append(finding)

    # Ordenar por score compuesto descendente
    scored.sort(key=lambda f: f['priority_score'], reverse=True)
    return scored
