# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
def invalidate_user_sessions(user_id, reason="manual_logout"):
    """Invalida todas las sesiones activas de un usuario.
    Se llama en logout, cambio de contraseña y deactivación de cuenta."""
    # Añadir el JTI del token actual a la blocklist en Redis
    jti = get_jwt()['jti']
    revocation_key = f"revoked_token:{jti}"
    # TTL igual al tiempo de vida del token para limpieza automática
    redis_client.setex(revocation_key, current_app.config['JWT_ACCESS_TOKEN_EXPIRES'], "1")

    # Marcar todos los refresh tokens del usuario como revocados en BD
    UserSession.query.filter_by(
        user_id=user_id,
        is_active=True
    ).update({'is_active': False, 'revoked_at': datetime.now(timezone.utc),
              'revocation_reason': reason})
    db.session.commit()

    audit_log('SESSION_INVALIDATED', user_id=user_id,
             severity='INFO', details=f"Razón: {reason}")
