# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
ri_coverage = ce.get_reservation_coverage(
    TimePeriod={"Start": "2026-03-01", "End": "2026-03-31"},
    Granularity="MONTHLY",
    GroupBy=[{"Type": "DIMENSION", "Key": "INSTANCE_TYPE"}]
)

for group in ri_coverage["CoveragesByTime"][0]["Groups"]:
    instance_type = group["Attributes"]["instanceType"]
    coverage = group["Coverage"]["CoverageHours"]["CoverageHoursPercentage"]
    print(f"{instance_type}: {coverage}% cubierto por RI")
