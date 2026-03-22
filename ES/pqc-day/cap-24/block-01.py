# Extraído de: LibroPQC/cap-24-saas.md
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.models.organization import Organization
from app.models.client import Client
from app.models.analysis import AnalysisJob
from sqlalchemy import func, extract
from datetime import datetime


def check_plan_limit(limit_type):
    """Decorador que verifica límites del plan antes de ejecutar la acción.

    Uso:
        @check_plan_limit('clients')    # Antes de crear un cliente
        @check_plan_limit('users')      # Antes de crear un usuario
        @check_plan_limit('analyses')   # Antes de lanzar un análisis
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            org = Organization.query.get(user.organization_id)

            if limit_type == 'clients':
                current = Client.query.filter_by(
                    organization_id=org.id,
                    status='active'
                ).count()
                maximum = org.max_clients
                resource = 'clientes'

            elif limit_type == 'users':
                current = User.query.filter_by(
                    organization_id=org.id,
                    is_active=True
                ).count()
                maximum = org.max_users
                resource = 'usuarios'

            elif limit_type == 'analyses':
                now = datetime.utcnow()
                current = AnalysisJob.query.filter(
                    AnalysisJob.organization_id == org.id,
                    extract('year', AnalysisJob.created_at) == now.year,
                    extract('month', AnalysisJob.created_at) == now.month
                ).count()
                maximum = org.max_analyses_per_month
                resource = 'análisis este mes'

            # Plan enterprise: sin límites numéricos
            if org.subscription_plan == 'enterprise':
                return f(*args, **kwargs)

            if current >= maximum:
                return jsonify({
                    'error': 'Plan limit reached',
                    'message': f'Has alcanzado el máximo de {maximum} '
                               f'{resource} para el plan '
                               f'{org.subscription_plan}.',
                    'current_plan': org.subscription_plan,
                    'limit': maximum,
                    'current_usage': current,
                    'upgrade_hint': _next_plan(org.subscription_plan)
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def _next_plan(current):
    """Devuelve el plan inmediatamente superior."""
    upgrade_path = {
        'free': 'starter',
        'starter': 'professional',
        'professional': 'enterprise'
    }
    next_plan = upgrade_path.get(current, None)
    if next_plan:
        return f'Actualiza a {next_plan} para aumentar tus límites.'
    return None
