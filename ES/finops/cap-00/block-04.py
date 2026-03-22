# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
rightsizing = ce.get_rightsizing_recommendation(
    Service="AmazonEC2",
    Configuration={
        "RecommendationTarget": "SAME_INSTANCE_FAMILY",
        "BenefitsConsidered": True
    }
)

for rec in rightsizing["RightsizingRecommendations"]:
    instance_id = rec["CurrentInstance"]["ResourceId"]
    savings = rec["ModifyRecommendationDetail"]["TargetInstances"][0][
        "EstimatedMonthlySavings"
    ]["Amount"]
    print(f"{instance_id}: ahorro estimado ${savings}/mes")
