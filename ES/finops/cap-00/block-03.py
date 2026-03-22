# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
forecast = ce.get_cost_forecast(
    TimePeriod={
        "Start": datetime.now().strftime("%Y-%m-%d"),
        "End": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    },
    Metric="UNBLENDED_COST",
    Granularity="MONTHLY"
)

predicted = float(forecast["Total"]["Amount"])
print(f"Forecast próximo mes: ${predicted:.2f}")
