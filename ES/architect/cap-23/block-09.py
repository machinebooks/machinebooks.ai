# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
def get_dashboard_kpis(period: str) -> dict:
    """
    Calcula los KPIs principales para el dashboard.
    Los valores actuales se contrastan con el período anterior
    para calcular la variación (positiva o negativa).
    """
    current = _get_period_metrics(period)
    prev_period = _previous_period(period)
    previous = _get_period_metrics(prev_period)

    def pct_change(current_val: float, prev_val: float) -> float | None:
        if prev_val == 0:
            return None  # Sin baseline: variación indefinida
        return round((current_val - prev_val) / prev_val * 100, 1)

    return {
        'arr': {
            'value': current['arr'],
            'change_pct': pct_change(current['arr'], previous['arr']),
            'trend': 'up' if current['arr'] >= previous['arr'] else 'down'
        },
        'mrr': {
            'value': current['mrr'],
            'change_pct': pct_change(current['mrr'], previous['mrr']),
            'trend': 'up' if current['mrr'] >= previous['mrr'] else 'down'
        },
        'pipeline_value': {
            'value': current['pipeline_value'],
            'change_pct': pct_change(
                current['pipeline_value'], previous['pipeline_value']
            )
        },
        'avg_close_velocity_days': current['avg_close_velocity_days'],
        'win_rate': current['win_rate'],
        'active_clients': current['active_clients'],
        # Alertas basadas en umbrales configurables
        'alerts': _compute_dashboard_alerts(current, previous)
    }
