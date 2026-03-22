# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
def platform_guard(f):
    """Capa 1: Verifica JWT y extrae claims del usuario.
    Verifica contra BD — NUNCA confía solo en el token.
    Se aplica a TODOS los endpoints protegidos."""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        claims = get_jwt()
        current_user_id = get_jwt_identity()

        # Verificar claims contra BD — NUNCA confiar solo en el token
        membership = db.session.query(UserAppMembership).join(
            App, UserAppMembership.app_id == App.id
        ).filter(
            UserAppMembership.user_id == current_user_id,
            App.app_code == claims.get('app_code', 'operations'),
            UserAppMembership.is_active == True  # Nota: .is_(True) es más idiomático en SQLAlchemy, pero == True también funciona
        ).first()

        if not membership:
            audit_log('ACCESS_DENIED', severity='WARNING',
                     details=f"No membership for user {current_user_id} "
                             f"in app {claims.get('app_code')}")
            return jsonify({"error": "Sin acceso a esta aplicación"}), 403

        # Inyectar contexto verificado contra BD — no claims del token
        g.current_user_id = current_user_id
        g.app_code = membership.app_code
        g.user_role = membership.role.name
        g.is_admin = membership.role.is_admin  # De BD, nunca del JWT — como documentamos en los errores reales al final del capítulo

        return f(*args, **kwargs)
    return decorated

def require_permission(module, action):
    """Capa 2: Verifica permiso específico por módulo y acción.
    Ejemplo: @require_permission('proposals', 'write')"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.is_admin:
                return f(*args, **kwargs)

            permissions = get_user_permissions(g.current_user_id, g.app_code)
            allowed_actions = permissions.get(module, [])

            if action not in allowed_actions:
                audit_log('ACCESS_DENIED', severity='WARNING',
                         details=f"{module}.{action} denied for "
                                 f"user {g.current_user_id}")
                return jsonify({"error": "Permiso insuficiente"}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
