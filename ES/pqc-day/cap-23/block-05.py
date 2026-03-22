# Extraído de: LibroPQC/cap-23-observabilidad.md
from datetime import timedelta
from sqlalchemy import func


@audit_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_audit_stats():
    """Estadísticas agregadas de actividad del sistema.
    Devuelve: total, hoy, semana, desglose por acción,
    desglose por tipo de entidad, usuarios activos 24h,
    actividad diaria últimos 7 días."""
    # Conteos generales
    total = AuditLog.query.count()

    today = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_count = AuditLog.query.filter(
        AuditLog.created_at >= today
    ).count()

    week_ago = datetime.utcnow() - timedelta(days=7)
    week_count = AuditLog.query.filter(
        AuditLog.created_at >= week_ago
    ).count()

    # Desglose por acción (top 10)
    actions = db.session.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.action) \
     .order_by(desc('count')).limit(10).all()

    # Desglose por tipo de entidad (top 10)
    entity_types = db.session.query(
        AuditLog.entity_type,
        func.count(AuditLog.id).label('count')
    ).filter(AuditLog.entity_type.isnot(None)) \
     .group_by(AuditLog.entity_type) \
     .order_by(desc('count')).limit(10).all()

    # Usuarios activos en las últimas 24 horas
    day_ago = datetime.utcnow() - timedelta(hours=24)
    active_users = db.session.query(
        func.count(func.distinct(AuditLog.user_id))
    ).filter(
        AuditLog.created_at >= day_ago,
        AuditLog.user_id.isnot(None)
    ).scalar()

    # Actividad diaria (últimos 7 días) para gráficos
    daily = db.session.query(
        func.date(AuditLog.created_at).label('date'),
        func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.created_at >= week_ago
    ).group_by(
        func.date(AuditLog.created_at)
    ).order_by('date').all()

    return jsonify({
        'total': total,
        'today': today_count,
        'week': week_count,
        'active_users_24h': active_users or 0,
        'actions': [
            {'action': a[0], 'count': a[1]} for a in actions
        ],
        'entity_types': [
            {'entity_type': e[0], 'count': e[1]}
            for e in entity_types
        ],
        'daily_activity': [
            {'date': str(d[0]), 'count': d[1]} for d in daily
        ]
    }), 200
