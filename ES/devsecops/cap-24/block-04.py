# Extraído de: LibroDevSecOps/cap-24-security-champions.md
from dataclasses import dataclass

@dataclass
class DeveloperMetrics:
    name: str
    team: str
    # Interacción con seguridad
    findings_reviewed: int        # Hallazgos revisados en 90 días
    findings_resolved: int        # Hallazgos resueltos en 90 días
    security_comments_on_prs: int # Comentarios de seguridad en PRs
    # Cobertura de código
    files_owned: int              # Ficheros donde es contributor principal
    critical_service_files: int   # De esos, cuántos en servicios críticos
    # Influencia técnica
    reviews_given: int            # Code reviews realizadas en 90 días
    reviews_accepted: int         # Reviews cuyas sugerencias se adoptaron

def calculate_champion_score(m: DeveloperMetrics) -> dict:
    """Calcula el champion score con tres dimensiones."""

    # Dimensión 1: Afinidad con seguridad (0-40 puntos)
    security_affinity = min(40, (
        m.findings_reviewed * 2 +
        m.findings_resolved * 5 +
        m.security_comments_on_prs * 3
    ))

    # Dimensión 2: Cobertura de superficie de ataque (0-30 puntos)
    if m.files_owned > 0:
        critical_ratio = m.critical_service_files / m.files_owned
    else:
        critical_ratio = 0
    attack_surface = min(30, int(critical_ratio * 30) + min(10, m.files_owned))

    # Dimensión 3: Influencia técnica (0-30 puntos)
    if m.reviews_given > 0:
        acceptance_rate = m.reviews_accepted / m.reviews_given
    else:
        acceptance_rate = 0
    influence = min(30, int(acceptance_rate * 20) + min(10, m.reviews_given // 5))

    total = security_affinity + attack_surface + influence

    return {
        "developer": m.name,
        "team": m.team,
        "total_score": total,
        "breakdown": {
            "security_affinity": security_affinity,
            "attack_surface": attack_surface,
            "technical_influence": influence
        },
        "recommendation": (
            "Candidato fuerte" if total >= 65
            else "Candidato viable" if total >= 40
            else "No recomendado en esta iteración"
        )
    }
