# Source: The FinOps Engineer and the Machine -- Chapter 1
# Pattern: AWS Cost Explorer daily cost fetcher

# services/cloud_cost_fetcher.py
import boto3
from datetime import datetime, timedelta

def fetch_aws_daily_costs(
    start_date: str, end_date: str
) -> list[dict]:
    """Queries AWS Cost Explorer. Inherent delay of ~24h."""
    ce = boto3.client("ce", region_name="eu-west-1")
    response = ce.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[
            {"Type": "DIMENSION", "Key": "SERVICE"}
        ],
    )
    results = []
    for day in response["ResultsByTime"]:
        date = day["TimePeriod"]["Start"]
        for group in day["Groups"]:
            results.append({
                "date": date,
                "provider": "aws",
                "service": group["Keys"][0],
                "cost_usd": float(
                    group["Metrics"]["UnblendedCost"]["Amount"]
                ),
            })
    return results
