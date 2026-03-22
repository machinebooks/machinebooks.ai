# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# Petición de exportación para auditoría externa
curl -X GET \
  "https://api.plataforma.ejemplo.com/api/v1/audit/export/csv" \
  "?start_date=2025-01-01T00:00:00" \
  "&end_date=2025-12-31T23:59:59" \
  "&decision_relevant_only=true" \
  "&risk_category=medium,high" \
  -H "Authorization: Bearer <TOKEN_AUDITOR>" \
  -o "audit_export_2025.csv"
