# Extraído de: LibroPQC/cap-23-observabilidad.md
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from datetime import datetime

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')


@audit_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Consulta paginada de registros de auditoría con filtros.
    Parámetros: page, per_page, action, entity_type,
                user_id, date_from, date_to, search
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = AuditLog.query

    # Filtros exactos
    action = request.args.get('action')
    if action:
        query = query.filter(AuditLog.action == action)

    entity_type = request.args.get('entity_type')
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    user_id = request.args.get('user_id', type=int)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    # Filtro por rango de fechas
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

    # Búsqueda de texto libre (escapar comodines SQL)
    search = request.args.get('search', '')
    if search:
        # Sanitizar caracteres especiales de LIKE para evitar
        # inyección de patrones: % y _ son comodines SQL
        safe_search = (
            search.replace('%', r'\%').replace('_', r'\_')
        )
        query = query.filter(
            db.or_(
                AuditLog.action.ilike(f'%{safe_search}%'),
                AuditLog.entity_type.ilike(f'%{safe_search}%'),
                AuditLog.ip_address.ilike(f'%{safe_search}%')
            )
        )

    # Orden cronológico inverso y paginación
    query = query.order_by(desc(AuditLog.created_at))
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'data': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    }), 200
