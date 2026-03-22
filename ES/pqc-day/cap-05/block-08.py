# Extraído de: LibroPQC/cap-05-modelo-datos.md
class FindingControlMapping(db.Model):
    """Mapeo entre hallazgos y controles: el puente entre técnica y compliance"""
    __tablename__ = 'finding_control_mappings'

    id = db.Column(db.Integer, primary_key=True)
    finding_type = db.Column(db.String(50), nullable=False)  # 'crypto', 'vulnerability'
    finding_id = db.Column(db.Integer, nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey(
                           'compliance_controls.id'), nullable=False)

    mapping_type = db.Column(db.Enum('violation', 'partial', 'recommendation'),
                             default='violation')
    confidence = db.Column(db.Float)           # 0.0 - 1.0
    notes = db.Column(db.Text)
    is_auto_mapped = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
