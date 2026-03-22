# Extraído de: LibroFinOps/cap-18-business-case-cfo.md
    def _build_scenarios(
        self, base_cost: float, base_value: float,
    ) -> list:
        """Proyección a 12 meses para los tres escenarios."""
        configs = [
            BusinessCaseScenario("optimista", 1.0, 1.0, 0.10),
            BusinessCaseScenario("base", 0.85, 0.95, 0.15),
            BusinessCaseScenario("conservador", 0.65, 0.85, 0.08),
        ]
        results = []
        for cfg in configs:
            cost, value = base_cost, (
                base_value * cfg.productivity_capture_factor
                * cfg.acceptance_rate_factor
            )
            total_cost = total_value = 0.0
            for _ in range(12):
                cost *= (1 + cfg.growth_rate_monthly)
                value *= (1 + cfg.growth_rate_monthly)
                total_cost += cost
                total_value += value
            results.append({
                "scenario": cfg.name,
                "year1_cost_eur": round(total_cost, 2),
                "year1_value_eur": round(total_value, 2),
                "year1_net_eur": round(total_value - total_cost, 2),
            })
        return results
