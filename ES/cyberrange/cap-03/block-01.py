# Extraído de: LibroCyberrange/cap-03-arquitecto-cyber-range.md
# Sistema RBAC con 6 roles y principio de mínimo privilegio
# Ejemplo didáctico: patrones/auth/rbac.py

from functools import wraps
from flask import abort, g

class Role:
    """Roles del Cyber Range con permisos explícitos."""
    ADMIN = "admin"          # Gestión completa de la plataforma
    RED = "red_team"         # Acceso a VMs de ataque, submit flags
    BLUE = "blue_team"       # Acceso a VMs de defensa, herramientas SOC
    PURPLE = "purple_team"   # Acceso a ambos entornos, visión completa
    ORGANIZER = "organizer"  # Diseño y gestión de ejercicios
    VIEWER = "viewer"        # Solo lectura: scoreboards, dashboards

# Permisos por rol — cada acción requiere un permiso explícito
ROLE_PERMISSIONS = {
    Role.ADMIN: {"*"},  # Acceso total
    Role.ORGANIZER: {
        "exercise.create", "exercise.manage", "exercise.evaluate",
        "scenario.create", "scenario.deploy", "scenario.delete",
        "workzone.create", "workzone.manage",
        "user.invite", "user.assign_role",
        "report.generate", "report.export",
        "flag.create", "flag.manage",
    },
    Role.RED: {
        "vm.access_own", "flag.submit",
        "scenario.view_own", "scoreboard.view",
        "console.vnc_own",
    },
    Role.BLUE: {
        "vm.access_own", "flag.submit",
        "scenario.view_own", "scoreboard.view",
        "console.vnc_own", "siem.access_own",
    },
    Role.PURPLE: {
        "vm.access_own", "flag.submit",
        "scenario.view_all", "scoreboard.view",
        "console.vnc_own", "siem.access_own",
        "attack_log.view",
    },
    Role.VIEWER: {
        "scoreboard.view", "report.view",
    },
}

def require_permission(permission: str):
    """Decorador que verifica permisos antes de ejecutar el endpoint."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_role = g.current_user.role
            user_perms = ROLE_PERMISSIONS.get(user_role, set())

            # Admin tiene acceso total
            if "*" in user_perms:
                return f(*args, **kwargs)

            if permission not in user_perms:
                # Registrar intento de acceso no autorizado
                audit_log(
                    action="UNAUTHORIZED_ACCESS_ATTEMPT",
                    user_id=g.current_user.id,
                    detail=f"Permiso requerido: {permission}",
                    severity="WARNING"
                )
                abort(403, description="Permiso insuficiente")

            return f(*args, **kwargs)
        return wrapper
    return decorator
