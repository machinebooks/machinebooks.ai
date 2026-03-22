# Extraído de: LibroConsultor/cap-24-cuando-no-usar-ia.md
from enum import Enum
from dataclasses import dataclass

class AIZone(Enum):
    GREEN = "green"    # IA recomendada: análisis de datos, borradores, búsqueda
    YELLOW = "yellow"  # IA como borrador, revisión humana profunda obligatoria
    ORANGE = "orange"  # IA solo para datos de soporte, narrativa 100% humana
    RED = "red"        # IA prohibida: presencia humana completa

@dataclass
class TaskAssessment:
    zone: AIZone
    rationale: str
    review_required: str  # "none", "peer", "senior", "partner"

def assess_task(
    involves_crisis: bool,
    politically_sensitive: bool,
    ethical_ambiguity: bool,
    client_facing: bool,
    precedent_exists: bool,
    contractual_restriction: bool,
    data_verification_possible: bool
) -> TaskAssessment:
    """Evalúa la zona de uso de IA para una tarea de consultoría.

    Regla: un solo criterio rojo envía toda la tarea a zona roja.
    Los criterios amarillos se acumulan: dos amarillos suben a naranja."""

    # Criterios de zona roja (cualquiera activa zona roja)
    if contractual_restriction:
        return TaskAssessment(
            AIZone.RED,
            "Restricción contractual: IA prohibida",
            "partner"
        )
    if involves_crisis and client_facing:
        return TaskAssessment(
            AIZone.RED,
            "Comunicación de crisis: presencia humana requerida",
            "partner"
        )
    if ethical_ambiguity and not precedent_exists:
        return TaskAssessment(
            AIZone.RED,
            "Dilema ético sin precedente: juicio humano exclusivo",
            "partner"
        )

    # Criterios de zona naranja
    yellow_count = sum([
        politically_sensitive,
        client_facing and not data_verification_possible,
        not precedent_exists
    ])

    if yellow_count >= 2:
        return TaskAssessment(
            AIZone.ORANGE,
            "Múltiples factores de riesgo: IA solo para datos",
            "senior"
        )

    # Criterios de zona amarilla
    if politically_sensitive or client_facing:
        return TaskAssessment(
            AIZone.YELLOW,
            "Sensibilidad moderada: borrador IA + revisión profunda",
            "senior"
        )

    # Zona verde por defecto
    return TaskAssessment(
        AIZone.GREEN,
        "Tarea analítica estándar: IA recomendada",
        "peer"
    )
