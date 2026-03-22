# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
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

# Cada elemento en ResultsByTime contiene los grupos con su coste
for day in response["ResultsByTime"]:
    for group in day["Groups"]:
        service = group["Keys"][0]
        cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if cost > 1.0:  # Filtrar servicios con coste mínimo
            print(f"{day['TimePeriod']['Start']} | {service}: ${cost:.2f}")
