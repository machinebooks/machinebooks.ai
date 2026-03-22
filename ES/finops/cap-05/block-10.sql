# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
-- Gasto mensual por equipo en GCP
SELECT
  labels.value AS team,
  SUM(cost) AS total_cost,
  SUM(IFNULL(credits.amount, 0)) AS total_credits,
  SUM(cost) + SUM(IFNULL(credits.amount, 0)) AS net_cost
FROM
  `proyecto-billing.billing_export.gcp_billing_export_v1_*`
LEFT JOIN UNNEST(labels) AS labels
  ON labels.key = 'team'
LEFT JOIN UNNEST(credits) AS credits
WHERE
  invoice.month = '202603'
GROUP BY team
ORDER BY net_cost DESC
