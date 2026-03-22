# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
ce = boto3.client("ce", region_name="us-east-1")

sp_utilization = ce.get_savings_plans_utilization(
    TimePeriod={"Start": "2026-03-01", "End": "2026-03-31"},
    Granularity="MONTHLY"
)

total = sp_utilization["Total"]
print(f"Utilización Savings Plans: {total['Utilization']['UtilizationPercentage']}%")
print(f"Ahorro neto: ${total['Savings']['NetSavings']}")
