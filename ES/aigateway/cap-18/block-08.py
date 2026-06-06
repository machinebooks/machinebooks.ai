# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Promote: genera par RSA + Shamir split + persist shares (KeyEscrowService)
async def create_master_key(
    self, *, team_id, scope, admin_passwords: dict[int, str],
    threshold: int = 2, created_by: int,
) -> CreateMekResult:
    # N (total de shares) = número de admins firmantes, no un valor fijo
    total = len(admin_passwords)
    # 1. Generar par RSA-4096
    priv = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    pub_pem = priv.public_key().public_bytes(PEM, SubjectPublicKeyInfo)

    # 2. Shamir split de la privada serializada
    priv_pem = priv.private_bytes(PEM, PKCS8, NoEncryption())
    shares = shamir_split(priv_pem, threshold, total)

    # 3. Cifrar cada share con la password del admin titular
    for i, (admin_id, password) in enumerate(admin_passwords.items()):
        salt = secrets.token_bytes(32)
        kek = _scrypt_kek(password, salt)       # scrypt → KEK de 32 bytes
        ct, nonce, tag = _aes_gcm_encrypt(kek, shares[i])
        # INSERT master_key_shares(kid, share_index, holder_admin_id, ...)
