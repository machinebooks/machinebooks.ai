# Source: The FinOps Engineer and the Machine -- Appendix B
# Pattern: Azure Cost Management examples

from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient

# DefaultAzureCredential tries, in order:
#   1. Environment variables (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET)
#   2. Managed Identity (on Azure)
#   3. Azure CLI login (in development)
credential = DefaultAzureCredential()
client = CostManagementClient(credential)

from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import (
    QueryDefinition, QueryTimePeriod, QueryDataset,
    QueryAggregation, QueryGrouping
)
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = CostManagementClient(credential)

scope = "/subscriptions/<YOUR_SUBSCRIPTION_ID>"

query = QueryDefinition(
    type="ActualCost",
    timeframe="Custom",
    time_period=QueryTimePeriod(
        from_property="2026-03-01T00:00:00Z",
        to="2026-03-31T23:59:59Z"
    ),
    dataset=QueryDataset(
        granularity="Daily",
        aggregation={
            "totalCost": QueryAggregation(
                name="Cost", function="Sum"
            )
        },
        grouping=[
            QueryGrouping(type="Dimension", name="ServiceName")
        ]
    )
)

result = client.query.usage(scope=scope, parameters=query)

for row in result.rows:
    cost, service, date = row[0], row[1], row[2]
    if cost > 1.0:
        print(f"{date} | {service}: ${cost:.2f}")
