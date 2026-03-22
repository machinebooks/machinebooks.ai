# Extraído de: LibroPQC/cap-15-nis2.md
class ComplianceControl(db.Model):
    """Control individual dentro de un marco normativo"""
    __tablename__ = 'compliance_controls'

    id = db.Column(db.Integer, primary_key=True)
    framework_id = db.Column(db.Integer,
                             db.ForeignKey('compliance_frameworks.id',
                                           ondelete='CASCADE'), nullable=False)
    reference = db.Column(db.String(50), nullable=False)    # 'NIS2.RISK.8'
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    guidance = db.Column(db.Text)                           # Guía de implementación

    # Jerarquía recursiva: un control puede tener subcontroles
    parent_control_id = db.Column(db.Integer,
                                  db.ForeignKey('compliance_controls.id'),
                                  nullable=True)
    category = db.Column(db.String(100))    # 'Technical', 'Organizational'
    domain = db.Column(db.String(200))      # 'Gestión de Riesgos'
    is_mandatory = db.Column(db.Boolean, default=True)
    sequence_order = db.Column(db.Integer, default=0)

    # Motor de mapeo automático
    keywords = db.Column(db.Text)           # JSON: ["cryptography", "cifrado", "PQC"]
    pqc_relevant = db.Column(db.Boolean, default=False)
    cloud_relevant = db.Column(db.Boolean, default=False)

    # Auto-referencia para la jerarquía
    children = db.relationship('ComplianceControl',
                               backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic')
