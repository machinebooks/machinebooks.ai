# Extraído de: LibroPQC/cap-05-modelo-datos.md
class AnalysisTarget(db.Model):
    """Punto de escaneo concreto dentro de un job"""
    __tablename__ = 'analysis_targets'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('analysis_jobs.id',
                       ondelete='CASCADE'), nullable=False)

    target_type = db.Column(db.Enum('repository', 'database', 'cloud_service',
                            'domain', 'api', name='target_types'), nullable=False)
    target_identifier = db.Column(db.String(500), nullable=False)
    target_metadata = db.Column(db.JSON)
    analysis_status = db.Column(db.Enum('pending', 'scanning', 'completed',
                                'failed', name='analysis_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
