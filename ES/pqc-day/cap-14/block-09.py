# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
@ai_admin_bp.route('/roi/dashboard', methods=['GET'])
@jwt_required()
def roi_dashboard():
    """ROI de la IA: coste real vs. valor generado
    por ahorro de tiempo de analista."""
    # ...
    calls = stats.calls or 0
    # Parámetros conservadores de estimación
    analyst_hourly_rate = 80    # EUR/hora
    minutes_saved_per_call = 20  # minutos ahorrados por llamada IA

    hours_saved = calls * minutes_saved_per_call / 60
    value_generated = hours_saved * analyst_hourly_rate
    cost = stats.total_cost or 0
    roi_ratio = round(value_generated / max(cost, 0.01), 1)

    return jsonify({
        'roi': {
            'total_cost_usd': round(cost, 4),
            'estimated_hours_saved': round(hours_saved, 1),
            'estimated_value_eur': round(value_generated, 2),
            'roi_ratio': roi_ratio,
            'cost_per_call_usd': round(
                cost / max(calls, 1), 6),
        }
    })
