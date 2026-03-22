# Extraído de: LibroCISO/cap-27-executive-dashboard.md
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ExecutiveDashboardService:
    """Vista ejecutiva GRC — agrega KPIs de todos los módulos."""

    def __init__(self, db: AsyncSession, corporate_id: int):
        self.db = db
        self.cid = corporate_id

    async def _count(self, model, *extra_filters) -> int:
        """Helper: cuenta registros con filtro multi-tenant."""
        filters = [
            model.corporate_id == self.cid,
            model.is_deleted == False,
            *extra_filters,
        ]
        r = await self.db.execute(
            select(func.count(model.id)).where(*filters)
        )
        return r.scalar() or 0

    async def get_dashboard(self) -> dict:
        """Retorna KPIs agregados de todos los módulos GRC."""

        # ─── TPRM (Capítulo 9) ──────────────────────────
        total_suppliers = await self._count(Supplier)
        critical_suppliers = await self._count(
            Supplier, Supplier.criticality == "critical"
        )
        open_findings = await self._count(
            SupplierFinding,
            SupplierFinding.status.in_(["open", "overdue"])
        )

        avg_score_q = await self.db.execute(
            select(func.avg(Supplier.risk_score)).where(
                Supplier.corporate_id == self.cid,
                Supplier.is_deleted == False,
                Supplier.risk_score.isnot(None)
            )
        )
        avg_supplier_score = avg_score_q.scalar()

        # ─── NIS2 (Capítulo 9) ──────────────────────────
        nis2_total = await self._count(NIS2Requirement)
        nis2_compliant = await self._count(
            NIS2Requirement,
            NIS2Requirement.status == "compliant"
        )
        nis2_score = round(
            nis2_compliant / max(nis2_total, 1) * 100, 1
        )

        # ─── Cyber Risk (Capítulo 7) ────────────────────
        var95_q = await self.db.execute(
            select(func.sum(CyberRiskScenario.ale_p95)).where(
                CyberRiskScenario.corporate_id == self.cid,
                CyberRiskScenario.is_deleted == False,
                CyberRiskScenario.ale_p95.isnot(None)
            )
        )
        cyber_var_95 = var95_q.scalar() or 0

        # ─── Policy & Awareness (Capítulo 26) ───────────
        total_policies = await self._count(SecurityPolicy)
        published = await self._count(
            SecurityPolicy,
            SecurityPolicy.status == "published"
        )

        avg_click_q = await self.db.execute(
            select(func.avg(PhishingSimulation.click_rate)).where(
                PhishingSimulation.corporate_id == self.cid,
                PhishingSimulation.is_deleted == False,
                PhishingSimulation.click_rate.isnot(None)
            )
        )
        avg_phishing_click = avg_click_q.scalar()

        avg_culture_q = await self.db.execute(
            select(func.avg(SecurityCultureScore.overall_score)).where(
                SecurityCultureScore.corporate_id == self.cid,
                SecurityCultureScore.is_deleted == False
            )
        )
        avg_culture = avg_culture_q.scalar()

        # ─── AI Governance (Capítulo 14) ─────────────────
        total_ai_models = await self._count(AIModelDiscovery)
        high_risk_ai = await self._count(
            AIModelDiscovery,
            AIModelDiscovery.is_high_risk == True
        )

        # ─── Compliance Frameworks (Capítulo 8) ─────────
        frameworks_q = await self.db.execute(
            select(
                ComplianceFramework.name,
                ComplianceFramework.compliance_score
            ).where(
                ComplianceFramework.corporate_id == self.cid,
                ComplianceFramework.is_deleted == False
            )
        )
        frameworks = [
            {"name": r[0], "score": r[1]}
            for r in frameworks_q.all()
        ]

        # ─── Overall GRC Score ───────────────────────────
        scores = []
        if avg_supplier_score:
            scores.append(avg_supplier_score)
        if nis2_score > 0:
            scores.append(nis2_score)
        if avg_culture:
            scores.append(avg_culture)
        for f in frameworks:
            if f["score"]:
                scores.append(f["score"])

        overall = (
            round(sum(scores) / max(len(scores), 1), 1)
            if scores else None
        )

        return {
            "overall_grc_score": overall,
            "tprm": {
                "total_suppliers": total_suppliers,
                "critical_suppliers": critical_suppliers,
                "avg_supplier_score": (
                    round(avg_supplier_score, 1)
                    if avg_supplier_score else None
                ),
                "open_findings": open_findings,
            },
            "nis2": {
                "compliance_score": nis2_score,
                "total_requirements": nis2_total,
                "compliant": nis2_compliant,
            },
            "cyber_risk": {
                "cyber_var_95_eur": round(cyber_var_95, 0),
            },
            "policy_awareness": {
                "total_policies": total_policies,
                "published_policies": published,
                "avg_phishing_click_rate": (
                    round(avg_phishing_click, 1)
                    if avg_phishing_click else None
                ),
                "avg_culture_score": (
                    round(avg_culture, 1)
                    if avg_culture else None
                ),
            },
            "ai_governance": {
                "total_ai_models": total_ai_models,
                "high_risk_models": high_risk_ai,
            },
            "compliance_frameworks": frameworks,
        }
