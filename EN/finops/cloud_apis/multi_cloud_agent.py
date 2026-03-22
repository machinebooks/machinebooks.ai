# Source: The FinOps Engineer and the Machine -- Appendix B
# Pattern: Multi-cloud cost agent with Claude

import anthropic
import boto3
import json
from datetime import datetime, timedelta

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

# Define tools the agent can invoke
tools = [
    {
        "name": "get_aws_costs",
        "description": "Query AWS costs by service for a given period",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back"
                }
            },
            "required": ["days"]
        }
    }
]

def handle_tool_call(tool_name, tool_input):
    """Execute the tool requested by the agent."""
    if tool_name == "get_aws_costs":
        ce = boto3.client("ce", region_name="us-east-1")
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=tool_input["days"])).strftime("%Y-%m-%d")
        response = ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
        )
        return json.dumps(response, default=str)

# The agent reasons over cost data
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "Analyze AWS costs for the last 7 days and identify anomalies"
    }]
)
