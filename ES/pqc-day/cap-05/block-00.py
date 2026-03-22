# Extraído de: LibroPQC/cap-05-modelo-datos.md
class CryptoFinding(db.Model):
    """Hallazgo criptográfico: el átomo del inventario PQC"""
    __tablename__ = 'crypto_findings'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('analysis_jobs.id',
                       ondelete='CASCADE'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('analysis_targets.id',
                          ondelete='CASCADE'), nullable=False)

    # Clasificación del hallazgo
    finding_type = db.Column(db.Enum(
        'algorithm',       # RSA-2048 en código fuente
        'protocol',        # TLS 1.2 con cipher suite vulnerable
        'certificate',     # Certificado X.509 con ECDSA-P256
        'key',             # Clave SSH RSA-4096
        'configuration',   # Configuración de KMS con RSA
        name='finding_types'), nullable=False)

    algorithm_name = db.Column(db.String(100))    # RSA-2048, ECDSA-P256, AES-256
    algorithm_category = db.Column(db.String(50))  # asymmetric, symmetric, hash
    risk_level = db.Column(db.Enum(
        'critical', 'high', 'medium', 'low', 'info',
        name='risk_levels'), nullable=False)

    # El campo más importante de toda la base de datos
    pqc_compliant = db.Column(db.Boolean, default=False)

    # Contexto del hallazgo
    location = db.Column(db.Text)        # Ruta, URL o identificador
    context = db.Column(db.Text)         # JWT, TLS, cifrado en reposo, SSH...
    description = db.Column(db.Text)     # Descripción legible
    recommendation = db.Column(db.Text)  # "Migrar a ML-KEM-768"
    cve_reference_links = db.Column(db.JSON)  # CVEs y referencias

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
