# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
# Lógica de control de acceso por rol
def can_user_access_challenge(challenge, user):
    """Verificar si un usuario puede acceder a un challenge
    basado en su rol y configuración de visibilidad"""
    if not challenge.visibility:
        return True  # Sin restricciones configuradas

    user_role = getattr(user, 'role', 'viewer')

    if user_role == 'admin':
        return True  # Administradores: acceso total
    elif user_role == 'organizer':
        return True  # Organizadores: supervisión completa
    elif user_role == 'red':
        return challenge.visibility.get('red_team', False)
    elif user_role == 'blue':
        return challenge.visibility.get('blue_team', False)
    elif user_role == 'purple':
        return challenge.visibility.get('purple_team', False)
    else:
        return False  # Viewers: sin acceso a challenges
