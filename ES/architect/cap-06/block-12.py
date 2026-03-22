# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
class CredentialVault(db.Model):
    """Almacenamiento seguro de credenciales para automatización RPA.
    AES-256-GCM (cifrado autenticado), acceso auditado, rotación periódica."""
    __tablename__ = 'credential_vault'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)  # crm, portal, reporting
    credential_type = db.Column(db.String(50), nullable=False)  # password, token, cert
    encrypted_value = db.Column(db.LargeBinary, nullable=False)  # AES-256-GCM
    encryption_iv = db.Column(db.LargeBinary(12), nullable=False)  # Nonce 96 bits
    encryption_tag = db.Column(db.LargeBinary(16), nullable=False)  # Tag GCM
    encryption_key_id = db.Column(db.String(50), nullable=False)
    last_rotated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_accessed_at = db.Column(db.DateTime, nullable=True)
    access_count = db.Column(db.Integer, default=0)
