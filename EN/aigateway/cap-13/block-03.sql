# Extracted from: LibroAIGateway/cap-13-tenants-quotas.md
-- Example: monthly spending of user X in org Y
SELECT COALESCE(SUM(cost_usd), 0)
FROM audit_logs
WHERE organization_id = :org_id
  AND employee_id = :user_id
  AND created_at >= :month_start
  AND created_at < :month_end
  AND cost_usd IS NOT NULL;
