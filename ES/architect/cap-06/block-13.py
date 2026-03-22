# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
def enable_mfa(user_id):
    """Activa MFA para un usuario. Genera secreto cifrado y códigos de respaldo."""
    # Generar secreto OTP y cifrarlo con Fernet
    secret = pyotp.random_base32()
    fernet = Fernet(current_app.config['MFA_ENCRYPTION_KEY'])
    encrypted_secret = fernet.encrypt(secret.encode())

    # Generar 10 códigos de respaldo — SHA-256 con salt único, un solo uso
    backup_codes = []
    backup_hashes = []
    for _ in range(10):
        code = secrets.token_hex(4).upper()  # 8 caracteres hex
        salt = secrets.token_hex(16)         # Salt único de 32 caracteres
        hashed = hashlib.sha256((salt + code).encode()).hexdigest()
        backup_codes.append(code)
        backup_hashes.append(f"{salt}:{hashed}")  # Almacenar salt:hash

    user.mfa_secret = encrypted_secret
    user.mfa_backup_hashes = json.dumps(backup_hashes)
    user.mfa_enabled = True
    db.session.commit()

    audit_log('MFA_ENABLED', user_id=user_id, severity='INFO',
             details="MFA activado con 10 códigos de respaldo")

    # Los códigos se muestran UNA VEZ al usuario — nunca se guardan en claro
    return backup_codes
