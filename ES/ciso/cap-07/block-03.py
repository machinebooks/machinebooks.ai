# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
# Servicio de cálculo de riesgo — lógica condicionada por methodology

from typing import Optional
from dataclasses import dataclass


@dataclass
class RiskCalculationResult:
    """Resultado del cálculo de riesgo, cualitativo o cuantitativo."""
    inherent_risk_score: Optional[int] = None     # 1-25 (cualitativo)
    inherent_risk_level: Optional[str] = None      # "muy_bajo"..."crítico"
    residual_risk_score: Optional[int] = None      # 1-25 (cualitativo)
    residual_risk_level: Optional[str] = None
    fair_ale: Optional[float] = None               # EUR (FAIR)
    residual_fair_ale: Optional[float] = None      # EUR (FAIR)


# Escalas de nivel de riesgo — configurables por methodology
RISK_LEVELS = {
    "magerit_v3": {
        (1, 4): "muy_bajo",    # Riesgo 1-4: asumible
        (5, 8): "bajo",        # Riesgo 5-8: aceptable con vigilancia
        (9, 12): "medio",      # Riesgo 9-12: requiere plan
        (13, 19): "alto",      # Riesgo 13-19: requiere acción prioritaria
        (20, 25): "crítico",   # Riesgo 20-25: acción inmediata
    },
    "nist_sp_800_30": {
        (1, 4): "very_low",
        (5, 8): "low",
        (9, 12): "moderate",
        (13, 19): "high",
        (20, 25): "very_high",
    },
    # Cada metodología puede definir sus propios umbrales
}


def calculate_qualitative_risk(
    probability: int,
    impact: int,
    methodology: str
) -> RiskCalculationResult:
    """Calcula riesgo inherente para metodologías cualitativas.

    Fórmula base: riesgo = probabilidad × impacto.
    Los umbrales de nivel dependen de la metodología.
    """
    if not (1 <= probability <= 5 and 1 <= impact <= 5):
        raise ValueError("Probabilidad e impacto deben estar entre 1 y 5")

    score = probability * impact
    levels = RISK_LEVELS.get(methodology, RISK_LEVELS["magerit_v3"])

    level = "sin_clasificar"
    for (low, high), label in levels.items():
        if low <= score <= high:
            level = label
            break

    return RiskCalculationResult(
        inherent_risk_score=score,
        inherent_risk_level=level
    )


def calculate_magerit_impact(scenario) -> int:
    """Calcula impacto MAGERIT como el máximo de las dimensiones DICAT.

    MAGERIT valora el impacto en cinco dimensiones independientes.
    Para la matriz 5×5, usamos el valor máximo como impacto agregado.
    Esto es conservador: refleja el peor caso por dimensión.
    """
    dimensions = [
        scenario.impact_disponibilidad,
        scenario.impact_integridad,
        scenario.impact_confidencialidad,
        scenario.impact_autenticidad,
        scenario.impact_trazabilidad,
    ]
    # Filtrar None (dimensiones no valoradas) y escalar de 0-4 a 1-5
    valued = [d + 1 for d in dimensions if d is not None]
    return max(valued) if valued else 3  # Default: medio


def calculate_fair_risk(
    lef: float,
    lm_primary: float,
    lm_secondary: float
) -> RiskCalculationResult:
    """Calcula riesgo FAIR como Annual Loss Expectancy.

    ALE = LEF × (Primary Loss + Secondary Loss)

    Nota: un modelo FAIR completo usa distribuciones Monte Carlo.
    Esta es una aproximación determinista válida como primera iteración.
    La versión con simulación Monte Carlo requiere datos históricos
    que muchas organizaciones no tienen.
    """
    total_lm = lm_primary + lm_secondary
    ale = lef * total_lm

    return RiskCalculationResult(fair_ale=ale)


def calculate_residual_risk(
    inherent_score: int,
    control_effectiveness: float  # 0.0 a 1.0
) -> int:
    """Calcula riesgo residual ajustando por eficacia de controles.

    Fórmula simplificada:
    riesgo_residual = riesgo_inherente × (1 - eficacia_controles)

    La eficacia se calcula como promedio ponderado de los controles
    aplicados al escenario. Un control con eficacia 0.8 reduce el
    riesgo inherente en un 80%.

    Limitación: esta fórmula asume independencia entre controles,
    lo cual no siempre es cierto en la práctica. Dos controles
    complementarios pueden tener un efecto combinado diferente
    a la suma de sus eficacias individuales.
    """
    residual = inherent_score * (1 - min(control_effectiveness, 0.95))
    # Mínimo 1: siempre queda riesgo residual
    return max(1, round(residual))
