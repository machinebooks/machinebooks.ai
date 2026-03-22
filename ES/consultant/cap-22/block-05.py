# Extraído de: LibroConsultor/cap-22-unit-economics.md
def cumulative_roi_series(tracker: ROITracker) -> list:
    """Serie temporal de ROI acumulado para gráfico."""
    sorted_records = sorted(tracker.records, key=lambda r: r.start_date)
    series = []
    cumulative_ai_cost = 0.0
    cumulative_margin = 0.0

    for record in sorted_records:
        cumulative_ai_cost += record.ai_cost
        cumulative_margin += record.incremental_margin
        roi = (cumulative_margin / cumulative_ai_cost
               if cumulative_ai_cost > 0 else 0)
        series.append({
            "date": record.start_date.isoformat(),
            "cumulative_roi": round(roi, 2),
            "cumulative_ai_cost": round(cumulative_ai_cost, 2),
            "cumulative_margin": round(cumulative_margin, 2),
            "project_type": record.project_type,
        })
    return series
