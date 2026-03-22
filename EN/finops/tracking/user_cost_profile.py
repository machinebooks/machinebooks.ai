# Source: The FinOps Engineer and the Machine -- Chapter 3
# Pattern: User cost profiling (power/average/light)

# cost_report_generator.py — Complete TCO report construction
# Combines measured data (LLM, cloud) with estimates (people, overhead).

import json, yaml

def build_tco_report(
    db_url: str, cloud_config_path: str, manual_costs_path: str,
    start: str, end: str, active_users: int,
) -> TCOReport:
    """Builds the TCO report by combining the three data sources."""
    engine = create_engine(db_url, echo=False)

    # Layer 1: LLM API (exact measurement)
    llm = get_llm_costs_from_db(engine, start, end)

    # Layer 2: Cloud infrastructure (per-service measurement)
    with open(cloud_config_path) as f:
        cloud_cfg = yaml.safe_load(f)
    period_key = start[:7]
    services = cloud_cfg.get("monthly_costs", {}).get(period_key, {}).get("services", {})
    cloud_total = sum(float(s.get("cost_eur", 0)) for s in services.values())

    # Layers 3-5: People, tools, overhead (structured estimation)
    with open(manual_costs_path) as f:
        manual = yaml.safe_load(f)
    month_manual = manual.get("monthly", {}).get(period_key, {})

    report = TCOReport(
        period_start=start, period_end=end, active_users=active_users,
        llm_cost=llm.total_cost_eur, cloud_cost=cloud_total,
        people_cost=float(month_manual.get("people_eur", 0)),
        tools_cost=float(month_manual.get("tools_eur", 0)),
        overhead_cost=float(month_manual.get("overhead_eur", 0)),
        llm_detail=llm,
    )
    report.total_tco = sum([
        report.llm_cost, report.cloud_cost, report.people_cost,
        report.tools_cost, report.overhead_cost,
    ])
    if active_users > 0:
        report.cost_per_user = round(report.total_tco / active_users, 2)

    return report
