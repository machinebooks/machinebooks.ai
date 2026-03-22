# Extraído de: LibroDevSecOps/cap-25-madurez-devsecops.md
# assessment_engine.py — Motor de evaluación de madurez
from maturity_model import MATURITY_MODEL, Level, DomainAssessment

def evaluate_domain(
    domain: str,
    responses: dict[str, bool]    # criterion_id -> True/False
) -> DomainAssessment:
    """Evalúa un dominio y determina el nivel alcanzado."""
    achieved = Level.INEXISTENT
    criteria_met = {}

    for level_num in range(1, 5):  # Niveles 1 a 4
        level_criteria = MATURITY_MODEL.get(domain, {}).get(level_num, [])
        if not level_criteria:
            continue

        all_met = True
        for criterion in level_criteria:
            met = responses.get(criterion.id, False)
            criteria_met[criterion.id] = met
            if not met:
                all_met = False

        if all_met:
            achieved = Level(level_num)
        else:
            break  # No se puede saltar niveles

    return DomainAssessment(
        domain=domain,
        achieved_level=achieved,
        criteria_met=criteria_met,
    )

def calculate_global_score(
    assessments: list[DomainAssessment],
    weights: dict[str, float]
) -> float:
    """Calcula puntuación global ponderada (0.0 a 4.0)."""
    total = 0.0
    for assessment in assessments:
        weight = weights.get(assessment.domain, 1.0 / len(assessments))
        total += assessment.achieved_level * weight
    return round(total, 2)

# Ejemplo de uso
ENTERPRISE_AI_WEIGHTS = {
    "PS": 0.20, "VM": 0.20, "GOV": 0.15,
    "MR": 0.15, "AIS": 0.20, "CA": 0.10,
}
