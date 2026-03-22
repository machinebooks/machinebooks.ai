# Source: The FinOps Engineer and the Machine -- Appendix B
# Pattern: AWS Cost Explorer examples

import boto3

# Credentials via environment variables or IAM profile:
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
# Or via IAM role on EC2/ECS/Lambda (recommended in production)

ce = boto3.client("ce", region_name="us-east-1")

import boto3
from datetime import datetime, timedelta

ce = boto3.client("ce", region_name="us-east-1")

end = datetime.now().strftime("%Y-%m-%d")
start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

response = ce.get_cost_and_usage(
    TimePeriod={"Start": start, "End": end},
    Granularity="DAILY",
    Metrics=["UnblendedCost"],
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
)

# Each element in ResultsByTime contains groups with their cost
for day in response["ResultsByTime"]:
    for group in day["Groups"]:
        service = group["Keys"][0]
        cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if cost > 1.0:  # Filter services with minimal cost
            print(f"{day['TimePeriod']['Start']} | {service}: ${cost:.2f}")

forecast = ce.get_cost_forecast(
    TimePeriod={
        "Start": datetime.now().strftime("%Y-%m-%d"),
        "End": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    },
    Metric="UNBLENDED_COST",
    Granularity="MONTHLY"
)

predicted = float(forecast["Total"]["Amount"])
print(f"Next month forecast: ${predicted:.2f}")

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
    print(f"{instance_id}: estimated savings ${savings}/month")
