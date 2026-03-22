# Source: The FinOps Engineer and the Machine -- Appendix B
# Pattern: GCP BigQuery billing export

from google.cloud import bigquery

bq = bigquery.Client(project="<YOUR_PROJECT_ID>")

query = """
SELECT
    service.description AS service,
    SUM(cost) AS total_cost,
    SUM(credits.amount) AS credits
FROM `<YOUR_PROJECT_ID>.billing_dataset.gcp_billing_export_v1_<BILLING_ACCOUNT_ID>`
LEFT JOIN UNNEST(credits) AS credits
WHERE usage_start_time >= '2026-03-01'
  AND usage_start_time < '2026-04-01'
GROUP BY service
ORDER BY total_cost DESC
LIMIT 20
"""

results = bq.query(query)
for row in results:
    print(f"{row.service}: ${row.total_cost:.2f} (credits: ${row.credits:.2f})")
