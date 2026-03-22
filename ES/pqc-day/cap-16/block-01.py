# Extraído de: LibroPQC/cap-16-dora.md
"""
Motor de scoring DORA-PQC.
Calcula la puntuación de preparación criptográfica post-cuántica
de una entidad financiera cruzando hallazgos con controles DORA.
"""
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class PqcScore:
    """Puntuación multidimensional de preparación PQC."""
    shelf_life_score: float      # 0-100: riesgo por vida útil del dato
    exposure_score: float        # 0-100: exposición a captura HNDL
    severity_score: float        # 0-100: impacto de compromiso
    migration_score: float       # 0-100: dificultad de migración
    overall_score: float         # Ponderado configurable
    g7_deadline_days: int        # Días hasta límite G7 CEG (2030)
    risk_category: str           # "critical", "high", "medium", "low"

# Pesos por defecto (configurables por tenant)
DEFAULT_WEIGHTS = {
    "shelf_life": 0.30,
    "exposure": 0.25,
    "severity": 0.30,
    "migration": 0.15,
}

# Categorías de datos financieros y su vida útil típica (años)
FINANCIAL_DATA_SHELF_LIFE = {
    "payment_transactions": 10,
    "customer_records": 10,     # Directiva AML
    "mortgage_contracts": 30,
    "insurance_policies": 25,
    "investment_portfolios": 15,
    "interbank_messages": 7,
    "audit_trails": 10,
    "regulatory_reports": 7,
    "digital_signatures": 30,   # Validez legal a largo plazo
    "encryption_keys_master": 20,
}

def calculate_shelf_life_score(findings: list, data_categories: dict) -> float:
    """
    Calcula el score de vida útil.
    Hallazgos que protegen datos de larga vida puntúan más alto.
    """
    if not findings:
        return 0.0

    scores = []
    for finding in findings:
        # Determinar categoría del dato protegido
        category = finding.get("data_category", "general")
        shelf_years = data_categories.get(category, 5)

        # Calcular riesgo: si shelf_life + migration_time > años_hasta_CRQC
        # Usamos estimación conservadora de CRQC: 2035
        years_until_crqc = 2035 - datetime.now().year
        migration_years = finding.get("estimated_migration_years", 2)

        # Desigualdad de Mosca: x + y > z
        mosca_gap = (shelf_years + migration_years) - years_until_crqc
        if mosca_gap > 0:
            # Ya en riesgo según Mosca
            score = min(100, 60 + mosca_gap * 4)
        else:
            # Margen disponible, pero hay que planificar
            score = max(10, 60 - abs(mosca_gap) * 5)

        scores.append(score)

    return sum(scores) / len(scores)


def calculate_exposure_score(findings: list) -> float:
    """
    Calcula el score de exposición a captura HNDL.
    Servicios expuestos a internet puntúan más alto.
    """
    exposure_weights = {
        "internet_facing": 1.0,    # APIs públicas, banca online
        "partner_network": 0.7,    # SWIFT, TARGET2, redes interbancarias
        "internal_network": 0.3,   # Servicios internos
        "isolated": 0.1,           # Sistemas air-gapped
    }

    if not findings:
        return 0.0

    total = 0.0
    for finding in findings:
        network_zone = finding.get("network_zone", "internal_network")
        weight = exposure_weights.get(network_zone, 0.5)
        # Algoritmo quantum-vulnerable en zona expuesta
        if finding.get("algorithm_type") in ("RSA", "ECDSA", "ECDH", "DH"):
            total += 100 * weight
        elif finding.get("algorithm_type") in ("DES", "3DES", "RC4"):
            total += 80 * weight  # Vulnerable incluso sin cuántica
        else:
            total += 40 * weight

    return min(100, total / len(findings))


def calculate_overall_score(
    findings: list,
    data_categories: dict = None,
    weights: dict = None,
) -> PqcScore:
    """
    Calcula el score global DORA-PQC de una entidad.
    """
    if data_categories is None:
        data_categories = FINANCIAL_DATA_SHELF_LIFE
    if weights is None:
        weights = DEFAULT_WEIGHTS

    shelf = calculate_shelf_life_score(findings, data_categories)
    exposure = calculate_exposure_score(findings)
    # severity y migration se calculan con lógica análoga
    severity = _calculate_severity_score(findings)
    migration = _calculate_migration_score(findings)

    overall = (
        shelf * weights["shelf_life"]
        + exposure * weights["exposure"]
        + severity * weights["severity"]
        + migration * weights["migration"]
    )

    # Días hasta deadline G7 CEG (1 enero 2031)
    g7_deadline = date(2031, 1, 1)
    days_remaining = (g7_deadline - date.today()).days

    # Categoría de riesgo
    if overall >= 75:
        risk = "critical"
    elif overall >= 50:
        risk = "high"
    elif overall >= 25:
        risk = "medium"
    else:
        risk = "low"

    return PqcScore(
        shelf_life_score=round(shelf, 1),
        exposure_score=round(exposure, 1),
        severity_score=round(severity, 1),
        migration_score=round(migration, 1),
        overall_score=round(overall, 1),
        g7_deadline_days=max(0, days_remaining),
        risk_category=risk,
    )
