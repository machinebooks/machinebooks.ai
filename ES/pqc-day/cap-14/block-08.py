# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
@ai_admin_bp.route('/quality/metrics', methods=['GET'])
@jwt_required()
def quality_metrics():
    """Métricas de calidad de la IA: tasa de éxito, errores,
    latencias P50 y P95."""
    period = request.args.get('period', '7d')
    days = int(period.replace('d', '')) if 'd' in period else 7
    since = datetime.utcnow() - timedelta(days=days)

    stats = db.session.query(
        func.count(AIUsageLog.id).label('total'),
        func.sum(case(
            (AIUsageLog.status == 'success', 1), else_=0
        )).label('success'),
        func.sum(case(
            (AIUsageLog.status == 'error', 1), else_=0
        )).label('errors'),
        func.avg(AIUsageLog.latency_ms).label('avg_latency'),
    ).filter(AIUsageLog.created_at >= since).first()

    total = stats.total or 1
    return jsonify({
        'metrics': {
            'total_calls': stats.total or 0,
            'success_rate': round(
                (stats.success or 0) / total * 100, 2),
            'error_rate': round(
                (stats.errors or 0) / total * 100, 2),
            'avg_latency_ms': round(stats.avg_latency or 0, 0),
        }
    })
