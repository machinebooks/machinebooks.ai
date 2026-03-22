# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# services/risk_classifier.py
RISK_CLASSIFICATION_RULES = {
    # task_type → risk_category basado en el análisis del sistema
    "offer_generation": "low",         # genera documentos, no decisiones vinculantes
    "compliance_report": "medium",     # puede influir en decisiones regulatorias
    "risk_analysis": "medium",         # apoya decisiones de gestión de riesgos
    "legal_review": "high",            # análisis con implicaciones legales
    "contract_generation": "medium",   # genera documentos contractuales
    "simple_query": "low",             # consulta sin impacto decisional
    "cloud_cost_recommendation": "medium",  # recomendaciones con impacto económico
    "rightsizing_agent": "medium",     # agente que sugiere cambios en infra
}

def classify_interaction_risk(task_type: str) -> str:
    """
    Clasifica el riesgo de una interacción según el tipo de tarea.
    Default a 'medium' por precaución para tipos no clasificados.
    """
    return RISK_CLASSIFICATION_RULES.get(task_type, "medium")
