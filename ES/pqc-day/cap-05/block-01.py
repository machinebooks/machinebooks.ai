# Extraído de: LibroPQC/cap-05-modelo-datos.md
class VulnerabilityFinding(db.Model):
    """Vulnerabilidad complementaria con indicador de amenaza cuántica"""
    __tablename__ = 'vulnerability_findings'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('analysis_jobs.id',
                       ondelete='CASCADE'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('analysis_targets.id',
                          ondelete='CASCADE'), nullable=False)

    vulnerability_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.Enum('critical', 'high', 'medium', 'low', 'info',
                         name='severity_levels'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    affected_component = db.Column(db.String(255))

    # Vocabulario de vulnerabilidades estándar
    cwe_id = db.Column(db.String(20))         # CWE-327 (uso de crypto débil)
    cvss_score = db.Column(db.Numeric(3, 1))  # 7.5
    cvss_vector = db.Column(db.String(100))   # CVSS:3.1/AV:N/AC:L/...

    remediation = db.Column(db.Text)
    reference_links = db.Column(db.JSON)

    # ¿Se amplifica esta vulnerabilidad con computación cuántica?
    quantum_threat = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
