# Extraído de: LibroPQC/cap-05-modelo-datos.md
class ControlAssessment(db.Model):
    """Evaluación de un control concreto: manual, automática o por IA"""
    __tablename__ = 'control_assessments'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey(
        'compliance_assessments.id', ondelete='CASCADE'), nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey(
        'compliance_controls.id', ondelete='CASCADE'), nullable=False)

    implementation_status = db.Column(db.Enum(
        'not_assessed', 'not_implemented', 'partial',
        'implemented', 'not_applicable'), default='not_assessed')
    effectiveness_level = db.Column(db.Enum(
        'none', 'low', 'medium', 'high'), default='none')

    # Evidencias
    evidence_description = db.Column(db.Text)
    evidence_files = db.Column(db.Text)        # JSON: rutas a documentos

    # Hallazgos y recomendaciones del evaluador
    findings = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    gaps = db.Column(db.Text)

    # Origen de la evaluación
    source = db.Column(db.Enum(
        'manual', 'code_analysis', 'cloud_analysis',
        'document', 'questionnaire', 'ai_suggestion'), default='manual')
    source_finding_ids = db.Column(db.Text)    # JSON: IDs de findings

    # Sugerencia de la IA
    ai_suggested_status = db.Column(db.String(50))
    ai_confidence = db.Column(db.Float)         # 0.0 - 1.0
    ai_reasoning = db.Column(db.Text)
