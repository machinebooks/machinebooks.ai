# Source: The FinOps Engineer and the Machine -- Chapter 22
# Pattern: Cloud cost comparator agent

# agents/cloud_cost_comparator.py
import anthropic
import boto3
from datetime import datetime, timedelta


def compare_cloud_providers(period_days: int = 30) -> dict:
    """
    Compares infrastructure costs between cloud providers.
    Generates a normalized report for enterprise negotiation.
    """
    client = anthropic.Anthropic()
    end = datetime.utcnow().strftime("%Y-%m-%d")
    start = (datetime.utcnow() - timedelta(days=period_days)).strftime("%Y-%m-%d")

    # Get actual costs from AWS (if there are active workloads)
    ce = boto3.client("ce")
    aws_response = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    # Ask Claude to analyze and compare with Azure public prices
    analysis = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system="You are a FinOps analyst. Compare cloud costs between providers.",
        messages=[{
            "role": "user",
            "content": f"""AWS cost data for the last {period_days} days:
{aws_response['ResultsByTime']}

Compare these costs with equivalent Azure public prices.
For each service, indicate: current AWS cost, estimated Azure cost,
percentage difference, and negotiation recommendation.""",
        }],
    )
    return {
        "period": f"{start} to {end}",
        "aws_data": aws_response["ResultsByTime"],
        "analysis": analysis.content[0].text,
        "analysis_cost_usd": (
            analysis.usage.input_tokens * 3 / 1_000_000
            + analysis.usage.output_tokens * 15 / 1_000_000
        ),
    }
