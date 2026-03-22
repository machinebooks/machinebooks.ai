# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/models.py (continuación)

class ComplianceControl(BaseModel):
    """Control individual dentro de un marco."""
    __tablename__ = "compliance_controls"

    id = Column(Integer, primary_key=True)
    framework_id = Column(
        Integer,
        ForeignKey("compliance_frameworks.id"),
        nullable=False
    )
    parent_id = Column(
        Integer,
        ForeignKey("compliance_controls.id"),
        nullable=True  # NULL = control raíz o categoría
    )
    code = Column(String(50), nullable=False)      # "mp.com.2", "A.8.24"
    name = Column(String(300), nullable=False)
    description = Column(Text)
    guidance = Column(Text)  # Orientación para implementación
    level = Column(Integer, default=0)  # Nivel jerárquico: 0=categoría, 1=control

    # Estado de cumplimiento (evaluación del auditor/CISO)
    compliance_status = Column(
        SAEnum(ComplianceStatus),
        default=ComplianceStatus.NOT_ASSESSED
    )
    # Estado de implementación (progreso técnico)
    implementation_status = Column(
        SAEnum(ImplementationStatus),
        default=ImplementationStatus.NOT_STARTED
    )
    # Justificación de no aplicabilidad
    not_applicable_justification = Column(Text)

    # Para ENS: requisitos diferenciados por categoría
    # {"BASICA": "aplica", "MEDIA": "aplica+", "ALTA": "reforzado"}
    level_requirements = Column(JSON, nullable=True)

    # Relaciones
    framework = relationship("ComplianceFramework", back_populates="controls")
    parent = relationship(
        "ComplianceControl",
        remote_side=[id],
        backref="children"
    )
    evidences = relationship(
        "Evidence",
        back_populates="control",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("framework_id", "code", name="uq_framework_control"),
    )
