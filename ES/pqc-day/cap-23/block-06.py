# Extraído de: LibroPQC/cap-23-observabilidad.md
@audit_bp.route('/actions', methods=['GET'])
@jwt_required()
def get_audit_actions():
    """Devuelve la lista de acciones distintas registradas.
    Útil para poblar el desplegable de filtro en el frontend."""
    actions = db.session.query(
        AuditLog.action
    ).distinct().order_by(AuditLog.action).all()
    return jsonify({
        'data': [a[0] for a in actions]
    }), 200


@audit_bp.route('/entity-types', methods=['GET'])
@jwt_required()
def get_entity_types():
    """Devuelve la lista de tipos de entidad distintos."""
    types = db.session.query(
        AuditLog.entity_type
    ).filter(
        AuditLog.entity_type.isnot(None)
    ).distinct().order_by(AuditLog.entity_type).all()
    return jsonify({
        'data': [t[0] for t in types]
    }), 200
