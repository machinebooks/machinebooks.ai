# Extraído de: LibroPQC/cap-15-nis2.md
class FindingControlMapping(db.Model):
    """Registro auditable del mapeo hallazgo → control"""
    __tablename__ = 'finding_control_mappings'

    id = db.Column(db.Integer, primary_key=True)
    finding_type = db.Column(db.String(50), nullable=False)  # 'crypto', 'vulnerability'
    finding_id = db.Column(db.Integer, nullable=False)
    control_id = db.Column(db.Integer,
                           db.ForeignKey('compliance_controls.id'),
                           nullable=False)
    mapping_type = db.Column(db.Enum('violation', 'partial',
                                      'recommendation'), default='violation')
    confidence = db.Column(db.Float)          # 0.0 a 1.0
    notes = db.Column(db.Text)                # "Mapeado por keyword: rsa"
    is_auto_mapped = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
