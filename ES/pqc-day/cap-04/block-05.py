# Extraído de: LibroPQC/cap-04-requisito-arquitectura.md
# Ejemplo didáctico: patrones/utils/plan_limits.py
from flask_jwt_extended import get_jwt_identity
from app.models import Organization, User
from functools import wraps

class PlanLimitExceeded(Exception):
    """Excepción cuando se excede un límite del plan."""
    def __init__(self, resource: str, current_plan: str):
        self.resource = resource
        self.current_plan = current_plan
        super().__init__(
            f"Límite de {resource} alcanzado para el plan {current_plan}. "
            f"Considere actualizar su suscripción."
        )

def check_plan_limit(resource_type):
    """Decorador que verifica los límites del plan antes de ejecutar."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = User.query.get(get_jwt_identity())
            org = user.organization

            if resource_type == 'client' and not org.can_add_client():
                raise PlanLimitExceeded('clientes', org.subscription_plan)
            elif resource_type == 'user' and not org.can_add_user():
                raise PlanLimitExceeded('usuarios', org.subscription_plan)
            elif resource_type == 'analysis' and not org.can_run_analysis():
                raise PlanLimitExceeded('análisis mensuales', org.subscription_plan)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_feature(feature_name):
    """Decorador que verifica si una funcionalidad está habilitada."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = User.query.get(get_jwt_identity())
            org = user.organization
            features = org.features or {}

            if not features.get(feature_name, False):
                return {
                    "error": f"La funcionalidad '{feature_name}' "
                             f"no está incluida en su plan "
                             f"({org.subscription_plan}). "
                             f"Contacte con soporte para actualizar."
                }, 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
