# Extraído de: LibroConsultor/cap-24-cuando-no-usar-ia.md
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class AIIncident:
    """Registro de incidente por uso inadecuado de IA.

    Anónimo y orientado a aprendizaje, no a culpa.
    Se revisa mensualmente en la reunión de mejora de práctica."""

    timestamp: datetime = field(default_factory=datetime.now)

    # Categoría del fallo
    category: str = ""  # "hallucination", "overreliance", "wrong_zone",
                        # "client_trust", "quality_degradation"

    # Fase del proyecto donde ocurrió
    project_phase: str = ""  # "presale", "delivery", "review", "communication"

    # Impacto estimado
    impact: str = ""  # "none_detected", "rework_required",
                      # "client_dissatisfaction", "contract_loss"

    # Descripción anónima del incidente
    description: str = ""

    # Qué habría prevenido el incidente
    prevention: str = ""

    # Zona de la matriz que debería haberse aplicado
    correct_zone: str = ""  # "green", "yellow", "orange", "red"
    actual_zone_used: str = ""

# Análisis trimestral de incidentes
def analyze_incidents(incidents: list[AIIncident]) -> dict:
    """Genera informe trimestral de incidentes para mejora de práctica."""

    total = len(incidents)
    if total == 0:
        return {"message": "Sin incidentes registrados"}

    by_category = {}
    by_impact = {}
    zone_mismatches = 0

    for inc in incidents:
        by_category[inc.category] = by_category.get(inc.category, 0) + 1
        by_impact[inc.impact] = by_impact.get(inc.impact, 0) + 1
        if inc.correct_zone != inc.actual_zone_used:
            zone_mismatches += 1

    return {
        "total_incidents": total,
        "by_category": by_category,
        "by_impact": by_impact,
        "zone_mismatch_rate": zone_mismatches / total,
        # Métrica crítica: qué porcentaje de incidentes
        # se habría evitado aplicando la matriz correctamente
        "preventable_rate": zone_mismatches / total
    }
