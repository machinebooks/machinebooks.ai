# Source: The FinOps Engineer and the Machine -- Chapter 21
# Pattern: AI Act risk level classifier

# services/risk_classifier.py
RISK_CLASSIFICATION_RULES = {
    # task_type → risk_category based on system analysis
    "offer_generation": "low",         # generates documents, not binding decisions
    "compliance_report": "medium",     # may influence regulatory decisions
    "risk_analysis": "medium",         # supports risk management decisions
    "legal_review": "high",            # analysis with legal implications
    "contract_generation": "medium",   # generates contractual documents
    "simple_query": "low",             # query with no decisional impact
    "cloud_cost_recommendation": "medium",  # recommendations with economic impact
    "rightsizing_agent": "medium",     # agent that suggests infrastructure changes
}

def classify_interaction_risk(task_type: str) -> str:
    """
    Classifies the risk of an interaction by task type.
    Defaults to 'medium' as a precaution for unclassified types.
    """
    return RISK_CLASSIFICATION_RULES.get(task_type, "medium")
