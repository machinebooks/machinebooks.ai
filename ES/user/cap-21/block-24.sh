# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
# Listar instancias en GCP
gcloud compute instances list \
  --format="table(name, zone, machineType.basename(),
    status, networkInterfaces[0].accessConfigs[0].natIP)"

# Costes (requiere BigQuery billing export configurado)
bq query --use_legacy_sql=false '
  SELECT service.description, SUM(cost) as total_cost
  FROM `proyecto.dataset.gcp_billing_export_v1_XXXXXX`
  WHERE DATE(usage_start_time) >= "2026-03-01"
  GROUP BY 1
  ORDER BY total_cost DESC
  LIMIT 20'
