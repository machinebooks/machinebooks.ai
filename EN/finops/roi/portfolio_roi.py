# Source: The FinOps Engineer and the Machine -- Chapter 18
# Pattern: Portfolio-level ROI tracker

# services/portfolio_roi.py
class PortfolioROIConsolidator:
    """
    Consolidates ROI from multiple AI platforms.
    Requires each platform to use HumanBaseline.
    """
    def __init__(self, platform_databases: dict):
        self.platforms = platform_databases

    def consolidated_summary(self, days: int = 30) -> dict:
        total_cost = total_value = 0.0
        by_platform = {}

        for name, db in self.platforms.items():
            tracker = ROITracker(db)
            s = tracker.get_summary(days=days)
            cost = s.get("total_llm_cost_eur", 0)
            value = s.get("total_value_eur", 0)
            total_cost += cost
            total_value += value
            by_platform[name] = {
                "roi": s.get("roi_global", 0),
                "cost": cost, "value": value,
            }

        global_roi = (
            (total_value - total_cost) / total_cost
            if total_cost > 0 else 0
        )
        return {
            "portfolio_roi": round(global_roi, 1),
            "total_cost_eur": round(total_cost, 2),
            "total_value_eur": round(total_value, 2),
            "net_eur": round(total_value - total_cost, 2),
            "by_platform": by_platform,
        }
