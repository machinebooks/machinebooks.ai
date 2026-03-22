# Extraído de: LibroPQC/cap-18-roadmap.md
from typing import Dict, Any, List, Tuple


# Matriz de riesgo 5×5 con niveles definidos
RISK_MATRIX = {
    (1, 1): 'low',    (1, 2): 'low',    (1, 3): 'low',
    (1, 4): 'medium', (1, 5): 'medium',
    (2, 1): 'low',    (2, 2): 'low',    (2, 3): 'medium',
    (2, 4): 'medium', (2, 5): 'high',
    (3, 1): 'low',    (3, 2): 'medium', (3, 3): 'medium',
    (3, 4): 'high',   (3, 5): 'high',
    (4, 1): 'medium', (4, 2): 'medium', (4, 3): 'high',
    (4, 4): 'high',   (4, 5): 'critical',
    (5, 1): 'medium', (5, 2): 'high',   (5, 3): 'high',
    (5, 4): 'critical', (5, 5): 'critical',
}


def evaluate_risk_scenario(
    asset_name: str,
    asset_type: str,
    threat_description: str,
    vulnerability_description: str,
    inherent_likelihood: int,
    inherent_impact: int,
    controls_applied: List[str],
    residual_likelihood: int = None,
    residual_impact: int = None
) -> Dict[str, Any]:
    """
    Evalúa un escenario de riesgo criptográfico completo.

    Si no se proporcionan valores residuales, se estiman
    asumiendo que los controles aplicados reducen probabilidad
    e impacto en función de su tipo y cobertura.
    """
    # Validar rangos (1-5)
    for val, name in [
        (inherent_likelihood, 'inherent_likelihood'),
        (inherent_impact, 'inherent_impact')
    ]:
        if not 1 <= val <= 5:
            raise ValueError(f"{name} debe estar entre 1 y 5")

    # Calcular riesgo inherente
    inherent_score = inherent_likelihood * inherent_impact
    inherent_level = RISK_MATRIX.get(
        (inherent_likelihood, inherent_impact), 'medium'
    )

    # Estimar riesgo residual si no se proporciona
    if residual_likelihood is None:
        reduction = _estimate_control_effectiveness(controls_applied)
        residual_likelihood = max(1, inherent_likelihood - reduction['likelihood'])
        residual_impact = max(1, inherent_impact - reduction['impact'])

    residual_score = residual_likelihood * residual_impact
    residual_level = RISK_MATRIX.get(
        (residual_likelihood, residual_impact), 'medium'
    )

    # Determinar tratamiento recomendado
    treatment = _recommend_treatment(
        residual_level, inherent_score, residual_score
    )

    return {
        'asset_name': asset_name,
        'asset_type': asset_type,
        'threat_description': threat_description,
        'vulnerability_description': vulnerability_description,
        'inherent_likelihood': inherent_likelihood,
        'inherent_impact': inherent_impact,
        'inherent_risk_score': inherent_score,
        'inherent_risk_level': inherent_level,
        'residual_likelihood': residual_likelihood,
        'residual_impact': residual_impact,
        'residual_risk_score': residual_score,
        'residual_risk_level': residual_level,
        'treatment_option': treatment,
        'risk_reduction_percentage': round(
            (1 - residual_score / inherent_score) * 100, 1
        ) if inherent_score > 0 else 0,
        'controls_applied': controls_applied
    }


def _estimate_control_effectiveness(
    controls: List[str]
) -> Dict[str, int]:
    """
    Estima la reducción de probabilidad e impacto
    según los tipos de controles aplicados.

    Controles preventivos reducen probabilidad.
    Controles de detección y respuesta reducen impacto.
    """
    control_effects = {
        'crypto_migration': {'likelihood': 2, 'impact': 1},
        'monitoring': {'likelihood': 0, 'impact': 1},
        'network_segmentation': {'likelihood': 1, 'impact': 1},
        'access_control': {'likelihood': 1, 'impact': 0},
        'hybrid_crypto': {'likelihood': 1, 'impact': 2},
        'key_rotation': {'likelihood': 1, 'impact': 0},
        'data_classification': {'likelihood': 0, 'impact': 1},
    }

    total_likelihood_reduction = 0
    total_impact_reduction = 0

    for control in controls:
        effect = control_effects.get(control, {'likelihood': 0, 'impact': 0})
        total_likelihood_reduction += effect['likelihood']
        total_impact_reduction += effect['impact']

    # Limitar reducción máxima a 3 niveles
    return {
        'likelihood': min(total_likelihood_reduction, 3),
        'impact': min(total_impact_reduction, 3)
    }


def _recommend_treatment(
    residual_level: str,
    inherent_score: int,
    residual_score: int
) -> str:
    """
    Recomienda la opción de tratamiento según el riesgo residual.

    - critical / high → mitigate (migrar obligatoriamente)
    - medium → mitigate o transfer según contexto
    - low → accept (documentar y monitorizar)
    """
    if residual_level in ('critical', 'high'):
        return 'mitigate'
    elif residual_level == 'medium':
        # Si la reducción ha sido significativa, puede aceptarse
        if inherent_score > 0 and residual_score / inherent_score < 0.4:
            return 'accept'
        return 'mitigate'
    else:
        return 'accept'
