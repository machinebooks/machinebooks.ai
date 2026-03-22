# Extraído de: LibroFinOps/cap-19-unit-economics.md
# services/unit_economics.py — Método principal de cálculo
class UnitEconomicsCalculator:
    PROFILES = [
        UserProfile("power",   7_000_000, 15_000_000, 9.27, 0.15),
        UserProfile("average", 2_000_000,  7_000_000, 3.96, 0.60),
        UserProfile("light",           0,  2_000_000, 0.07, 0.25),
    ]
    INFRA_BASE_COST_EUR = 385.0
    TENANT_OVERHEAD_EUR = 0.80

    def __init__(self, db: Session):
        self.db = db

    def calculate(self, period_days: int = 30, tenant_id: Optional[int] = None):
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        query = (
            self.db.query(
                LLMUsageLog.user_id,
                func.sum(LLMUsageLog.total_tokens).label("total_tokens"),
                func.sum(LLMUsageLog.total_cost_usd).label("total_cost_usd"),
            )
            .filter(LLMUsageLog.created_at >= cutoff)
            .group_by(LLMUsageLog.user_id)
        )
        if tenant_id:
            query = query.filter(LLMUsageLog.tenant_id == tenant_id)

        users = query.all()
        # Clasificar cada usuario en un perfil y agregar costes
        profile_counts = {p.profile_name: 0 for p in self.PROFILES}
        profile_costs = {p.profile_name: 0.0 for p in self.PROFILES}
        total_cost = sum(u.total_cost_usd or 0 for u in users)

        for u in users:
            profile = self._classify_user(u.total_tokens or 0)
            profile_counts[profile] += 1
            profile_costs[profile] += u.total_cost_usd or 0

        active = len(users)
        avg_cost = total_cost / active if active else 0
        # ... construir y devolver UnitEconomicsReport
