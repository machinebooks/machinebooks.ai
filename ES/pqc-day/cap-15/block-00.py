# Extraído de: LibroPQC/cap-15-nis2.md
class ComplianceFramework(db.Model):
    """Marco normativo: NIS2, DORA, ISO 27001, NIST CSF 2.0..."""
    __tablename__ = 'compliance_frameworks'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # 'NIS2'
    name = db.Column(db.String(200), nullable=False)              # 'Directiva NIS2 (UE) 2022/2555'
    description = db.Column(db.Text)
    version = db.Column(db.String(20))     # '2022/2555'
    category = db.Column(db.String(50))    # 'Security'
    is_active = db.Column(db.Boolean, default=True)
    total_controls = db.Column(db.Integer, default=0)

    # Un framework tiene muchos controles y puede tener muchas evaluaciones
    controls = db.relationship('ComplianceControl', backref='framework',
                               lazy='dynamic', cascade='all, delete-orphan')
    assessments = db.relationship('ComplianceAssessment', backref='framework',
                                  lazy='dynamic')
