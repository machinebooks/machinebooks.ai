# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/routes/audit_routes.py — Consulta de auditoría
@audit_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Logs de auditoría con filtrado y paginación."""
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    # Solo org_owner y org_admin pueden consultar el audit trail
    if user.role not in ['org_owner', 'org_admin']:
        return jsonify({'error': 'Permisos insuficientes'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Filtrar siempre por organización del usuario
    query = AuditLog.query.filter(
        AuditLog.organization_id == user.organization_id
    )

    # Filtros opcionales
    action = request.args.get('action')
    if action:
        query = query.filter(AuditLog.action == action)

    entity_type = request.args.get('entity_type')
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    date_from = request.args.get('date_from')
    if date_from:
        query = query.filter(
            AuditLog.created_at >= datetime.fromisoformat(date_from)
        )

    date_to = request.args.get('date_to')
    if date_to:
        query = query.filter(
            AuditLog.created_at <= datetime.fromisoformat(date_to)
        )

    # Ordenar por más reciente y paginar
    query = query.order_by(desc(AuditLog.created_at))
    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'data': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })
