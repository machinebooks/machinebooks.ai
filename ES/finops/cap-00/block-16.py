# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
from google.cloud import bigquery

bq = bigquery.Client(project="<TU_PROJECT_ID>")

query = """
SELECT
    service.description AS servicio,
    SUM(cost) AS coste_total,
    SUM(credits.amount) AS creditos
FROM `<TU_PROJECT_ID>.billing_dataset.gcp_billing_export_v1_<BILLING_ACCOUNT_ID>`
LEFT JOIN UNNEST(credits) AS credits
WHERE usage_start_time >= '2026-03-01'
  AND usage_start_time < '2026-04-01'
GROUP BY servicio
ORDER BY coste_total DESC
LIMIT 20
"""

results = bq.query(query)
for row in results:
    print(f"{row.servicio}: ${row.coste_total:.2f} (créditos: ${row.creditos:.2f})")
