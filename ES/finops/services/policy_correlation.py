# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# services/policy_correlation.py
class PolicyCorrelationAnalyzer:
    """
    Correlaciona cambios de política con cambios en patrones de gasto.
    Útil para análisis post-mortem y verificación de cumplimiento.
    """

    def analyze_policy_impact(
        self,
        db: Session,
        policy_change_commit: str,
        days_before: int = 7,
        days_after: int = 7,
    ) -> dict:
        """
        Compara el gasto antes y después de un cambio de política.
        Permite evaluar el impacto real del cambio.
        """
        change = db.query(PolicyChangeLog).filter(
            PolicyChangeLog.rollback_commit == policy_change_commit
        ).first()

        if not change:
            return {"error": "Cambio de política no encontrado"}

        change_date = change.deployed_at
        cutoff_before = change_date - timedelta(days=days_before)
        cutoff_after = change_date + timedelta(days=days_after)

        spend_before = (
            db.query(func.sum(LLMUsageLog.total_cost_eur))
            .filter(
                LLMUsageLog.created_at >= cutoff_before,
                LLMUsageLog.created_at < change_date,
            )
            .scalar() or 0
        )

        spend_after = (
            db.query(func.sum(LLMUsageLog.total_cost_eur))
            .filter(
                LLMUsageLog.created_at >= change_date,
                LLMUsageLog.created_at < cutoff_after,
            )
            .scalar() or 0
        )

        change_pct = (
            (spend_after - spend_before) / spend_before * 100
            if spend_before > 0 else 0
        )

        return {
            "policy_change": policy_change_commit,
            "change_date": change_date.isoformat(),
            "spend_before_eur": round(spend_before, 2),
            "spend_after_eur": round(spend_after, 2),
            "change_pct": round(change_pct, 1),
            "interpretation": (
                f"El cambio de política "
                f"{'aumentó' if change_pct > 0 else 'redujo'} "
                f"el gasto un {abs(change_pct):.1f}% en los "
                f"{days_after} días siguientes."
            ),
        }
