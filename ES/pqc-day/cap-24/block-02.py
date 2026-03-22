# Extraído de: LibroPQC/cap-24-saas.md
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.models.organization import Organization


# Definición centralizada de features por plan
PLAN_FEATURES = {
    'free': {
        'code_analysis': True,
        'certificate_analysis': False,
        'cloud_analysis': False,
        'ai_semantic': False,
        'compliance_reports': False,
        'pdf_reports': False,
        'autonomous_agent': False,
        'api_access': False,
        'sso': False
    },
    'starter': {
        'code_analysis': True,
        'certificate_analysis': True,
        'cloud_analysis': False,
        'ai_semantic': False,
        'compliance_reports': False,
        'pdf_reports': True,
        'autonomous_agent': False,
        'api_access': False,
        'sso': False
    },
    'professional': {
        'code_analysis': True,
        'certificate_analysis': True,
        'cloud_analysis': True,
        'ai_semantic': True,
        'compliance_reports': True,
        'pdf_reports': True,
        'autonomous_agent': False,
        'api_access': False,
        'sso': False
    },
    'enterprise': {
        'code_analysis': True,
        'certificate_analysis': True,
        'cloud_analysis': True,
        'ai_semantic': True,
        'compliance_reports': True,
        'pdf_reports': True,
        'autonomous_agent': True,
        'api_access': True,
        'sso': True
    }
}


def require_feature(feature_name):
    """Decorador que verifica que la organización tiene
    la funcionalidad habilitada en su plan.

    Uso:
        @require_feature('cloud_analysis')
        @require_feature('autonomous_agent')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            org = Organization.query.get(user.organization_id)

            # Priorizar features personalizadas en BD
            org_features = org.features or {}

            # Si la feature está explícitamente definida en la org, usar esa
            if feature_name in org_features:
                enabled = org_features[feature_name]
            else:
                # Fallback a las features por defecto del plan
                plan_defaults = PLAN_FEATURES.get(
                    org.subscription_plan, {}
                )
                enabled = plan_defaults.get(feature_name, False)

            if not enabled:
                return jsonify({
                    'error': 'Feature not available',
                    'message': f'La funcionalidad "{feature_name}" '
                               f'no está incluida en el plan '
                               f'{org.subscription_plan}.',
                    'current_plan': org.subscription_plan,
                    'required_plan': _min_plan_for_feature(feature_name)
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def _min_plan_for_feature(feature_name):
    """Devuelve el plan mínimo que incluye esta funcionalidad."""
    for plan in ['free', 'starter', 'professional', 'enterprise']:
        if PLAN_FEATURES.get(plan, {}).get(feature_name, False):
            return plan
    return 'enterprise'
