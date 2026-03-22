# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
class AIGovernanceControl(db.Model):
    """Controles de gobernanza IA — marco C.VR.1 a C.VR.12."""
    __tablename__ = 'ai_governance_controls'

    id = db.Column(db.Integer, primary_key=True)
    control_id = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(100))     # 'Privacy', 'Access', 'DLP', 'Audit', 'Governance'
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    requirement = db.Column(db.Text)         # qué debe cumplirse
    status = db.Column(
        db.Enum('compliant', 'partial', 'non_compliant',
                'not_applicable', 'pending'),
        default='pending'
    )
    evidence = db.Column(db.Text)            # cómo se demuestra
    evidence_url = db.Column(db.String(1000))
    responsible = db.Column(db.String(200))  # rol responsable
    last_checked_at = db.Column(db.DateTime)
    next_check_at = db.Column(db.DateTime)
