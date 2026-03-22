# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
@analytics_bp.route('/heatmap', methods=['GET'])
@platform_guard
@require_permissions(['analytics_view'])
def get_heatmap():
    """
    Devuelve la matriz de scoring para el período solicitado.
    Si el período no tiene datos precalculados, devuelve 404 con
    indicación del último período disponible.
    """
    period = request.args.get('period', _current_period())
    include_detail = request.args.get('detail', 'false').lower() == 'true'

    # Validar que el período tiene formato correcto (YYYY-MM)
    if not re.match(r'^\d{4}-\d{2}$', period):
        return jsonify({'error': 'Formato de período inválido. Use YYYY-MM'}), 400

    scores = HeatmapScore.query.filter_by(period=period)\
                               .order_by(HeatmapScore.total_score.desc())\
                               .all()

    if not scores:
        last_available = _get_last_calculated_period()
        return jsonify({
            'error': f'No hay datos para {period}',
            'last_available_period': last_available
        }), 404

    matrix = _build_matrix(scores, include_detail)

    # Metadatos de vigencia para que el frontend muestre el timestamp
    last_calc = max(s.calculated_at for s in scores)

    return jsonify({
        'period': period,
        'matrix': matrix,
        'calculated_at': last_calc.isoformat(),
        'total_cells': len(scores),
        'weights_config': _get_active_weights()
    })
