# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
# Herramienta del agente de riesgo — calculate_risk_matrix
# Registrada como tool en el RiskAgent (Claude Agent SDK)

import anthropic
from typing import Any


def calculate_risk_matrix_tool(
    analysis_id: int,
    methodology: str,
    filters: dict | None = None
) -> dict[str, Any]:
    """Calcula la matriz de riesgo completa para un análisis dado.

    Herramienta del RiskAgent: consulta activos y escenarios,
    calcula riesgos inherentes y residuales, y devuelve un
    resumen priorizado que el agente puede interpretar.

    Args:
        analysis_id: ID del análisis de riesgos
        methodology: Metodología activa (condiciona el cálculo)
        filters: Filtros opcionales (asset_type, risk_level, status)

    Returns:
        Diccionario con matriz, estadísticas y escenarios priorizados
    """
    # Obtener escenarios del análisis
    scenarios = get_scenarios_for_analysis(analysis_id, filters)

    # Construir matriz 5×5
    matrix = [[0] * 5 for _ in range(5)]  # matrix[prob][impact] = count
    critical_scenarios = []
    untreated_high = []

    for scenario in scenarios:
        if methodology == "fair":
            # FAIR no usa matriz 5×5 — agrupa por rango de ALE
            continue

        p = scenario.probability or 3
        i = scenario.impact or 3
        matrix[p - 1][i - 1] += 1

        result = calculate_qualitative_risk(p, i, methodology)

        if result.inherent_risk_level in ("alto", "crítico", "high", "very_high"):
            critical_scenarios.append({
                "id": scenario.id,
                "name": scenario.name,
                "asset": scenario.asset.name,
                "risk_score": result.inherent_risk_score,
                "risk_level": result.inherent_risk_level,
                "has_treatment": scenario.treatment_strategy is not None,
            })

        # Escenarios altos sin plan de tratamiento
        if (result.inherent_risk_level in ("alto", "crítico", "high", "very_high")
                and scenario.treatment_strategy is None):
            untreated_high.append({
                "id": scenario.id,
                "name": scenario.name,
                "asset": scenario.asset.name,
                "risk_score": result.inherent_risk_score,
            })

    # Estadísticas agregadas
    total = len(scenarios)
    by_level = {}
    for s in scenarios:
        if s.probability and s.impact:
            r = calculate_qualitative_risk(s.probability, s.impact, methodology)
            by_level[r.inherent_risk_level] = by_level.get(
                r.inherent_risk_level, 0
            ) + 1

    return {
        "matrix": matrix,
        "total_scenarios": total,
        "by_risk_level": by_level,
        "critical_scenarios": sorted(
            critical_scenarios, key=lambda x: x["risk_score"], reverse=True
        ),
        "untreated_high_risks": untreated_high,
        "methodology": methodology,
    }
