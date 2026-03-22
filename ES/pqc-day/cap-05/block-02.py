# Extraído de: LibroPQC/cap-05-modelo-datos.md
class AnalysisJob(db.Model):
    """Contenedor de un análisis completo"""
    __tablename__ = 'analysis_jobs'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id',
                          ondelete='CASCADE'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('client_projects.id',
                           ondelete='CASCADE'))

    job_type = db.Column(db.Enum('full', 'code', 'database', 'cloud',
                         'network', 'custom', name='job_types'), nullable=False)
    status = db.Column(db.Enum('pending', 'running', 'completed', 'failed',
                       'cancelled', name='job_status'), default='pending')
    progress_percentage = db.Column(db.Integer, default=0)

    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    configuration = db.Column(db.JSON)     # Parámetros del análisis
    result_summary = db.Column(db.JSON)    # Estadísticas finales
    error_message = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id',
                           ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships: un job produce tres tipos de hallazgos
    targets = db.relationship('AnalysisTarget', backref='job',
                              lazy='dynamic', cascade='all, delete-orphan')
    crypto_findings = db.relationship('CryptoFinding', backref='job',
                                      lazy='dynamic', cascade='all, delete-orphan')
    vulnerability_findings = db.relationship('VulnerabilityFinding', backref='job',
                                             lazy='dynamic', cascade='all, delete-orphan')
    compliance_checks = db.relationship('ComplianceCheck', backref='job',
                                        lazy='dynamic', cascade='all, delete-orphan')
