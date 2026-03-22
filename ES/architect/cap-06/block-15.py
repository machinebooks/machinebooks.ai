# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
# Backend — validación del callback OAuth2
@auth_bp.route('/api/auth/oauth2/callback', methods=['POST'])
@platform_guard
def oauth2_callback():
    """Intercambia authorization code por tokens. Valida state contra CSRF."""
    data = request.get_json()

    # Verificar state parameter — previene CSRF en el flujo OAuth2
    # Flask session solo para flujo OAuth2 temporal — la API usa JWT stateless
    stored_state = session.pop('oauth2_state', None)
    if not hmac.compare_digest(data.get('state', ''),
                                stored_state or ''):
        audit_log('ACCESS_DENIED', severity='CRITICAL',
                 details="OAuth2 state mismatch — posible CSRF")
        return jsonify({"error": "State inválido"}), 403

    # Intercambiar authorization code + code_verifier por tokens
    token_response = requests.post(CRM_TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': data['code'],
        'code_verifier': data['code_verifier'],  # PKCE — nunca viaja en claro
        'redirect_uri': OAUTH2_REDIRECT_URI,
        'client_id': os.environ['CRM_CLIENT_ID'],
    }, timeout=10)

    if not token_response.ok:
        audit_log('AUTH_FAILED', severity='WARNING',
                 details=f"OAuth2 token exchange falló: {token_response.status_code}")
        return jsonify({"error": "Error de autorización"}), 401

    # Almacenar tokens cifrados en CredentialVault — no en sesión ni cookies
    store_oauth_tokens(g.current_user_id, token_response.json())
    audit_log('OAUTH2_CONNECTED', user_id=g.current_user_id, severity='INFO')
    return jsonify({"status": "connected"})
