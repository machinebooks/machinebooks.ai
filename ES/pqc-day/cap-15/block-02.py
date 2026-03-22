# Extraído de: LibroPQC/cap-15-nis2.md
class ComplianceAssessment(db.Model):
    """Evaluación de cumplimiento: un cliente contra un framework"""
    __tablename__ = 'compliance_assessments'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id',
                          ondelete='CASCADE'), nullable=False)
    framework_id = db.Column(db.Integer,
                             db.ForeignKey('compliance_frameworks.id'),
                             nullable=False)
    name = db.Column(db.String(200), nullable=False)
    assessment_date = db.Column(db.Date, nullable=False)
    assessor = db.Column(db.String(200))
    status = db.Column(db.Enum('draft', 'in_progress', 'completed',
                               'approved', 'archived'), default='draft')
    overall_score = db.Column(db.Float)     # 0-100

    # Estadísticas de cumplimiento
    total_controls = db.Column(db.Integer, default=0)
    implemented_controls = db.Column(db.Integer, default=0)
    partial_controls = db.Column(db.Integer, default=0)
    not_implemented_controls = db.Column(db.Integer, default=0)
    not_applicable_controls = db.Column(db.Integer, default=0)

    # Trazabilidad: qué análisis técnicos alimentaron esta evaluación
    imported_code_analysis_ids = db.Column(db.Text)   # JSON array
    imported_cloud_analysis_ids = db.Column(db.Text)  # JSON array
