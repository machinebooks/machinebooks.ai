# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
def calculate_funnel_metrics(period: str) -> list[dict]:
    """
    Calcula métricas de funnel para el período dado.
    La tasa de conversión entre etapas y la velocidad media se calculan
    a partir del historial de transiciones en la tabla OpportunityEvent.
    """
    stages = ['F1', 'F2', 'F3', 'F4', 'F5']
    result = []

    for i, stage in enumerate(stages):
        # Oportunidades que alcanzaron esta etapa en el período
        reached = db.session.execute(
            text("""
                SELECT COUNT(DISTINCT o.id) as count,
                       COALESCE(SUM(o.estimated_value), 0) as total_value
                FROM opportunities o
                JOIN opportunity_events oe ON o.id = oe.opportunity_id
                WHERE oe.new_stage = :stage
                  AND DATE_FORMAT(oe.created_at, '%Y-%m') = :period
            """),
            {'stage': stage, 'period': period}
        ).first()

        # Velocidad media: días desde la etapa anterior
        if i > 0:
            prev_stage = stages[i - 1]
            avg_days = db.session.execute(
                text("""
                    SELECT AVG(DATEDIFF(curr.created_at, prev.created_at))
                    FROM opportunity_events curr
                    JOIN opportunity_events prev
                      ON curr.opportunity_id = prev.opportunity_id
                     AND prev.new_stage = :prev_stage
                    WHERE curr.new_stage = :stage
                      AND DATE_FORMAT(curr.created_at, '%Y-%m') = :period
                """),
                {'stage': stage, 'prev_stage': prev_stage, 'period': period}
            ).scalar() or 0
        else:
            avg_days = 0

        # Tasa de conversión respecto a la etapa anterior
        conversion_rate = 0.0
        if i > 0 and result[-1]['opportunity_count'] > 0:
            conversion_rate = reached.count / result[-1]['opportunity_count']

        result.append({
            'stage': stage,
            'opportunity_count': reached.count,
            'total_value': float(reached.total_value),
            'conversion_rate': round(conversion_rate, 3),
            'avg_days_in_stage': round(float(avg_days), 1)
        })

    return result
