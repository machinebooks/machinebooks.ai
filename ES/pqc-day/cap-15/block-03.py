# Extraído de: LibroPQC/cap-15-nis2.md
class ControlAssessment(db.Model):
    """Evaluación de un control específico dentro de un assessment"""
    __tablename__ = 'control_assessments'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer,
                              db.ForeignKey('compliance_assessments.id',
                                            ondelete='CASCADE'), nullable=False)
    control_id = db.Column(db.Integer,
                           db.ForeignKey('compliance_controls.id',
                                         ondelete='CASCADE'), nullable=False)

    # Evaluación humana
    implementation_status = db.Column(db.Enum(
        'not_assessed', 'not_implemented', 'partial',
        'implemented', 'not_applicable'), default='not_assessed')
    effectiveness_level = db.Column(db.Enum(
        'none', 'low', 'medium', 'high'), default='none')

    # Evidencias y hallazgos
    evidence_description = db.Column(db.Text)
    findings = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    gaps = db.Column(db.Text)

    # Fuente de la evaluación
    source = db.Column(db.Enum(
        'manual', 'code_analysis', 'cloud_analysis',
        'document', 'questionnaire', 'ai_suggestion'), default='manual')
    source_finding_ids = db.Column(db.Text)   # JSON array de IDs

    # Sugerencias de IA — el auditor decide si las acepta
    ai_suggested_status = db.Column(db.String(50))
    ai_confidence = db.Column(db.Float)       # 0.0 a 1.0
    ai_reasoning = db.Column(db.Text)
