# Source: The FinOps Engineer and the Machine -- Chapter 19
# Pattern: Hybrid billing model calculator

# services/billing_calculator.py — Billing with hybrid model
class BillingCalculator:
    BASE_PRICE_EUR = 65.0
    INCLUDED_TOKENS_PER_USER_PER_DAY = 10_000
    OVERAGE_PRICE_EUR_PER_K_TOKENS = 0.01

    def calculate_monthly_bill(self, db: Session, tenant_id: int,
                                year: int, month: int) -> dict:
        days_in_month = monthrange(year, month)[1]
        active_users = self._count_active_users(db, tenant_id, year, month)
        included = active_users * self.INCLUDED_TOKENS_PER_USER_PER_DAY * days_in_month
        actual = self._count_total_tokens(db, tenant_id, year, month)
        overage = max(0, actual - included)
        overage_eur = (overage / 1000) * self.OVERAGE_PRICE_EUR_PER_K_TOKENS

        return {
            "base_eur": self.BASE_PRICE_EUR,
            "included_tokens": included,
            "actual_tokens": actual,
            "overage_tokens": overage,
            "overage_eur": round(overage_eur, 2),
            "total_eur": round(self.BASE_PRICE_EUR + overage_eur, 2),
        }
