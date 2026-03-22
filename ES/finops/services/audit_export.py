# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# services/audit_export.py (continuación del AuditExportService)
    def get_compliance_summary(self, tenant_id: Optional[int], days: int = 30) -> dict:
        """
        Resumen de compliance para auditoría interna.
        Detecta patrones anómalos: coste alto + calidad baja,
        interacciones de alto riesgo sin revisión, agentes sin aprobación.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = self.db.query(LLMUsageLog).filter(LLMUsageLog.created_at >= cutoff)
        if tenant_id:
            query = query.filter(LLMUsageLog.tenant_id == tenant_id)

        logs = query.all()
        if not logs:
            return {"message": "Sin registros en el periodo"}

        high_risk = [l for l in logs if l.risk_category == "high"]
        unreviewed_high = [r for r in high_risk if not r.requires_human_review]
        high_cost_low_quality = [
            l for l in logs
            if l.quality_score and l.quality_score < 0.5
            and l.total_cost_eur and l.total_cost_eur > 0.50
        ]
        # Agentes que ejecutaron sin aprobación humana
        unapproved_agents = [
            l for l in logs
            if l.agent_id and not l.execution_approved_by
        ]

        alerts = []
        if len(high_cost_low_quality) > 5:
            alerts.append({
                "type": "high_cost_low_quality",
                "severity": "medium",
                "count": len(high_cost_low_quality),
                "message": f"{len(high_cost_low_quality)} interacciones con coste "
                           f">€0,50 y calidad <0,50.",
            })
        if unreviewed_high:
            alerts.append({
                "type": "high_risk_without_review",
                "severity": "high",
                "count": len(unreviewed_high),
                "message": f"{len(unreviewed_high)} interacciones de alto riesgo "
                           f"sin revisión humana.",
            })
        if unapproved_agents:
            alerts.append({
                "type": "agent_without_approval",
                "severity": "high",
                "count": len(unapproved_agents),
                "message": f"{len(unapproved_agents)} recomendaciones de agente "
                           f"ejecutadas sin aprobación humana.",
            })

        return {
            "period_days": days,
            "total_interactions": len(logs),
            "decision_relevant_count": sum(1 for l in logs if l.decision_relevant),
            "high_risk_count": len(high_risk),
            "compliance_alerts": alerts,
        }
