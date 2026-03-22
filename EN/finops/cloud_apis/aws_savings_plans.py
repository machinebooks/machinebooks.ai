# Source: The FinOps Engineer and the Machine -- Appendix B
# Pattern: AWS Savings Plans and RI coverage queries

ce = boto3.client("ce", region_name="us-east-1")

sp_utilization = ce.get_savings_plans_utilization(
    TimePeriod={"Start": "2026-03-01", "End": "2026-03-31"},
    Granularity="MONTHLY"
)

total = sp_utilization["Total"]
print(f"Savings Plans utilization: {total['Utilization']['UtilizationPercentage']}%")
print(f"Net savings: ${total['Savings']['NetSavings']}")

ri_coverage = ce.get_reservation_coverage(
    TimePeriod={"Start": "2026-03-01", "End": "2026-03-31"},
    Granularity="MONTHLY",
    GroupBy=[{"Type": "DIMENSION", "Key": "INSTANCE_TYPE"}]
)

for group in ri_coverage["CoveragesByTime"][0]["Groups"]:
    instance_type = group["Attributes"]["instanceType"]
    coverage = group["Coverage"]["CoverageHours"]["CoverageHoursPercentage"]
    print(f"{instance_type}: {coverage}% covered by RI")
