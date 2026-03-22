# Extraído de: LibroPQC/cap-05-modelo-datos.md
class ComplianceFramework(db.Model):
    """Marco normativo: NIST PQC, NIS2, DORA, ISO 27001, CNSA 2.0"""
    __tablename__ = 'compliance_frameworks'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)   # 'NIS2', 'DORA'
    name = db.Column(db.String(200), nullable=False)               # 'NIS2 Directive'
    description = db.Column(db.Text)
    version = db.Column(db.String(20))                             # '2024'
    category = db.Column(db.String(50))                            # 'Security', 'Privacy'
    is_active = db.Column(db.Boolean, default=True)
    total_controls = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
