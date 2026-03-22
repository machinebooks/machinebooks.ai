# Source: The FinOps Engineer and the Machine -- Chapter 6
# Pattern: AWS Cost Categories for cost attribution

# services/aws_cost_categories.py
import boto3

def create_cost_category(category_name: str, rules: list[dict]) -> dict:
    """
    Creates a Cost Category in AWS Cost Explorer.
    Rules map resource tags to category values.
    Example: all resources with tag team=backend -> "Backend Team"
    """
    ce_client = boto3.client("ce", region_name="us-east-1")

    response = ce_client.create_cost_category_definition(
        Name=category_name,
        RuleVersion="CostCategoryExpression.v1",
        Rules=rules,
        DefaultValue="Unattributed",
    )

    return response["CostCategoryArn"]


def build_team_category_rules() -> list[dict]:
    """
    Builds Cost Category rules by team.
    One rule per 'team' tag value.
    """
    teams = {
        "backend": "Backend Team",
        "frontend": "Frontend Team",
        "data": "Data Team",
        "platform": "Platform Team",
        "security": "Security Team",
    }

    rules = []
    for tag_value, category_value in teams.items():
        rules.append({
            "Value": category_value,
            "Rule": {
                "Tags": {
                    "Key": "team",
                    "Values": [tag_value],
                    "MatchOptions": ["EQUALS"],
                }
            },
        })

    return rules


def get_cost_by_category(category_name: str, start_date: str, end_date: str) -> list[dict]:
    """
    Queries spend grouped by Cost Category for the given period.
    start_date and end_date in YYYY-MM-DD format.
    """
    ce_client = boto3.client("ce", region_name="us-east-1")

    response = ce_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[
            {
                "Type": "COST_CATEGORY",
                "Key": category_name,
            }
        ],
    )

    results = []
    for time_period in response["ResultsByTime"]:
        for group in time_period["Groups"]:
            results.append({
                "period": time_period["TimePeriod"]["Start"],
                "category_value": group["Keys"][0],
                "cost_usd": float(group["Metrics"]["UnblendedCost"]["Amount"]),
                "currency": group["Metrics"]["UnblendedCost"]["Unit"],
            })

    return results
