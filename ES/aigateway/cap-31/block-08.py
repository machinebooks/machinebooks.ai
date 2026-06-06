# Extraído de: LibroAIGateway/cap-31-adopcion-compliance-portal.md
# KPIs del dashboard — gateway/app/api/v1/compliance_portal.py:164-177
totals_q = f"""
    SELECT
        COUNT(*)                                          AS total_audits,
        COUNT(DISTINCT app_name)                          AS total_apps,
        AVG(score_global)                                 AS avg_score,
        SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS completed_count,
        SUM(findings_count)                               AS total_findings,
        SUM(kpi_riesgo_altos)                             AS total_riesgo_altos
    FROM v_compliance_audits
    WHERE {where}
"""
