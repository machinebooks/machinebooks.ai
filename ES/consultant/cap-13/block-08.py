# Extraído de: LibroConsultor/cap-13-gap-analysis.md
def calculate_compliance_metrics(
    gaps: list[GapFinding],
    frameworks: list[str],
) -> dict:
    """Calcula métricas de cumplimiento por framework."""
    metrics = {}

    for fw in frameworks:
        fw_gaps = [
            g for g in gaps
            if fw in g.affected_frameworks
            or g.control.framework == fw
        ]
        if not fw_gaps:
            continue

        total = len(fw_gaps)
        compliant = sum(
            1 for g in fw_gaps
            if g.current_level >= g.target_level
        )
        partial = sum(
            1 for g in fw_gaps
            if g.current_level.value >= g.target_level.value - 1
            and g.current_level < g.target_level
        )

        avg_maturity = sum(
            g.current_level.value for g in fw_gaps
        ) / total

        metrics[fw] = {
            "total_controls": total,
            "compliant": compliant,
            "partial": partial,
            "non_compliant": total - compliant - partial,
            "compliance_pct": round(compliant / total * 100, 1),
            "avg_maturity": round(avg_maturity, 2),
            "critical_gaps": sum(
                1 for g in fw_gaps
                if g.priority == "critica"
            ),
        }

    return metrics
