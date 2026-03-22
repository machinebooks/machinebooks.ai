# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/routes/audit_routes.py — Estadísticas de auditoría
@audit_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_audit_stats():
    """Estadísticas del audit trail para el panel de administración."""
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    if user.role not in ['org_owner', 'org_admin']:
        return jsonify({'error': 'Permisos insuficientes'}), 403

    today = datetime.utcnow().replace(hour=0, minute=0, second=0)
    week_ago = datetime.utcnow() - timedelta(days=7)

    # Consulta base: siempre filtrada por organización
    base_query = AuditLog.query.filter(
        AuditLog.organization_id == user.organization_id
    )

    # Conteos básicos
    total = base_query.count()
    today_count = base_query.filter(
        AuditLog.created_at >= today
    ).count()

    # Desglose por acción (top 10), filtrado por organización
    actions = base_query.with_entities(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.action).order_by(desc('count')).limit(10).all()

    # Usuarios activos en las últimas 24 horas
    day_ago = datetime.utcnow() - timedelta(hours=24)
    active_users = base_query.with_entities(
        func.count(func.distinct(AuditLog.user_id))
    ).filter(
        AuditLog.created_at >= day_ago,
        AuditLog.user_id.isnot(None)
    ).scalar()

    # Actividad diaria (últimos 7 días)
    daily = base_query.with_entities(
        func.date(AuditLog.created_at).label('date'),
        func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.created_at >= week_ago
    ).group_by(func.date(AuditLog.created_at)).all()

    return jsonify({
        'total': total,
        'today': today_count,
        'active_users_24h': active_users or 0,
        'actions': [{'action': a[0], 'count': a[1]} for a in actions],
        'daily_activity': [
            {'date': str(d[0]), 'count': d[1]} for d in daily
        ]
    })
