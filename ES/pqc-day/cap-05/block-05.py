# Extraído de: LibroPQC/cap-05-modelo-datos.md
class ComplianceControl(db.Model):
    """Control individual dentro de un framework, con jerarquía"""
    __tablename__ = 'compliance_controls'

    id = db.Column(db.Integer, primary_key=True)
    framework_id = db.Column(db.Integer, db.ForeignKey(
        'compliance_frameworks.id', ondelete='CASCADE'), nullable=False)
    reference = db.Column(db.String(50), nullable=False)   # 'Art.21.2.e', 'A.10.1'
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    guidance = db.Column(db.Text)                          # Guía de implementación

    # Jerarquía auto-referencial
    parent_control_id = db.Column(db.Integer,
                                  db.ForeignKey('compliance_controls.id'))

    category = db.Column(db.String(100))     # 'Organizational', 'Technical'
    domain = db.Column(db.String(200))       # 'Criptografía', 'Control de acceso'
    is_mandatory = db.Column(db.Boolean, default=True)
    sequence_order = db.Column(db.Integer, default=0)
    keywords = db.Column(db.Text)            # JSON de keywords para mapeo IA

    # Relevancia para el dominio PQC
    pqc_relevant = db.Column(db.Boolean, default=False)
    cloud_relevant = db.Column(db.Boolean, default=False)

    # Jerarquía
    children = db.relationship('ComplianceControl',
                               backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic')
