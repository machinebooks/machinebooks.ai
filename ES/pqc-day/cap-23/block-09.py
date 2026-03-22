# Extraído de: LibroPQC/cap-23-observabilidad.md
@ai_admin_bp.route('/usage/stats', methods=['GET'])
@jwt_required()
def get_ai_usage_stats():
    """Estadísticas de uso de IA: llamadas, tokens, coste,
    latencia por proveedor y período."""
    days = request.args.get('days', 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)

    # Métricas globales del período
    global_stats = db.session.query(
        func.count(AIUsageLog.id).label('calls'),
        func.sum(AIUsageLog.tokens_total).label('tokens'),
        func.sum(AIUsageLog.cost_usd).label('cost'),
        func.avg(AIUsageLog.latency_ms).label('avg_latency'),
    ).filter(AIUsageLog.created_at >= since).first()

    # Desglose por proveedor
    by_provider = db.session.query(
        AIProvider.name,
        func.count(AIUsageLog.id).label('calls'),
        func.sum(AIUsageLog.tokens_total).label('tokens'),
        func.sum(AIUsageLog.cost_usd).label('cost'),
    ).join(
        AIUsageLog,
        AIUsageLog.provider_id == AIProvider.id,
        isouter=True
    ).filter(
        AIUsageLog.created_at >= since
    ).group_by(AIProvider.name).all()

    # Tasa de error por proveedor
    for provider in AIProvider.query.filter_by(is_active=True):
        metrics = db.session.query(
            func.count(AIUsageLog.id).label('calls'),
            func.avg(AIUsageLog.latency_ms).label('avg_latency'),
            func.sum(
                case((AIUsageLog.status == 'error', 1), else_=0)
            ).label('errors'),
        ).filter(
            AIUsageLog.provider_id == provider.id,
            AIUsageLog.created_at >= since
        ).first()
        # ... construir respuesta con tasa de error

    return jsonify({
        'period_days': days,
        'total_calls': global_stats.calls or 0,
        'total_tokens': global_stats.tokens or 0,
        'total_cost_usd': round(global_stats.cost or 0, 4),
        'avg_latency_ms': round(global_stats.avg_latency or 0),
        'by_provider': [
            {
                'provider': p[0],
                'calls': p[1],
                'tokens': p[2] or 0,
                'cost_usd': round(p[3] or 0, 4)
            } for p in by_provider
        ]
    }), 200
