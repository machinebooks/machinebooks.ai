# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import (
    QueryDefinition, QueryTimePeriod, QueryDataset,
    QueryAggregation, QueryGrouping
)
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = CostManagementClient(credential)

scope = "/subscriptions/<TU_SUBSCRIPTION_ID>"

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
    coste, servicio, fecha = row[0], row[1], row[2]
    if coste > 1.0:
        print(f"{fecha} | {servicio}: ${coste:.2f}")
