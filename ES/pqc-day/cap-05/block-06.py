# Extraído de: LibroPQC/cap-05-modelo-datos.md
class ComplianceAssessment(db.Model):
    """Evaluación de cumplimiento para un cliente contra un framework"""
    __tablename__ = 'compliance_assessments'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id',
                          ondelete='CASCADE'), nullable=False)
    framework_id = db.Column(db.Integer, db.ForeignKey(
                             'compliance_frameworks.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    assessment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('draft', 'in_progress', 'completed',
                       'approved', 'archived'), default='draft')
    overall_score = db.Column(db.Float)      # 0-100

    # Estadísticas precalculadas
    total_controls = db.Column(db.Integer, default=0)
    implemented_controls = db.Column(db.Integer, default=0)
    partial_controls = db.Column(db.Integer, default=0)
    not_implemented_controls = db.Column(db.Integer, default=0)
    not_applicable_controls = db.Column(db.Integer, default=0)

    # IDs de análisis importados (trazabilidad)
    imported_code_analysis_ids = db.Column(db.Text)   # JSON array
    imported_cloud_analysis_ids = db.Column(db.Text)  # JSON array

    def calculate_scores(self):
        """Recalcula estadísticas desde los ControlAssessments"""
        assessments = self.control_assessments.all()
        self.total_controls = len(assessments)
        self.implemented_controls = sum(
            1 for a in assessments
            if a.implementation_status == 'implemented')
        self.partial_controls = sum(
            1 for a in assessments
            if a.implementation_status == 'partial')
        self.not_implemented_controls = sum(
            1 for a in assessments
            if a.implementation_status == 'not_implemented')
        self.not_applicable_controls = sum(
            1 for a in assessments
            if a.implementation_status == 'not_applicable')

        applicable = self.total_controls - self.not_applicable_controls
        if applicable > 0:
            # Implementado = 100%, Parcial = 50%, No implementado = 0%
            score = (self.implemented_controls * 100
                     + self.partial_controls * 50) / applicable
            self.overall_score = round(score, 2)
