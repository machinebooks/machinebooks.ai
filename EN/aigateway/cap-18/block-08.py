# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# Promote: generates RSA pair + Shamir split + persists shares (KeyEscrowService)
async def create_master_key(
    self, *, team_id, scope, admin_passwords: dict[int, str],
    threshold: int = 2, created_by: int,
) -> CreateMekResult:
    # N (total shares) = number of signing admins, not a fixed value
    total = len(admin_passwords)
    # 1. Generate RSA-4096 pair
    priv = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    pub_pem = priv.public_key().public_bytes(PEM, SubjectPublicKeyInfo)

    # 2. Shamir split of serialized private key
    priv_pem = priv.private_bytes(PEM, PKCS8, NoEncryption())
    shares = shamir_split(priv_pem, threshold, total)

    # 3. Encrypt each share with the holder admin's password
    for i, (admin_id, password) in enumerate(admin_passwords.items()):
        salt = secrets.token_bytes(32)
        kek = _scrypt_kek(password, salt)       # scrypt → 32-byte KEK
        ct, nonce, tag = _aes_gcm_encrypt(kek, shares[i])
        # INSERT master_key_shares(kid, share_index, holder_admin_id, ...)
