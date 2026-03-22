# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/models.py (continuación)

class EvidenceType(str, enum.Enum):
    DOCUMENT = "document"          # Política, procedimiento, acta
    SCREENSHOT = "screenshot"      # Captura de pantalla de configuración
    CONFIGURATION = "configuration"  # Fichero de configuración exportado
    LOG = "log"                    # Extracto de log o auditoría
    CERTIFICATE = "certificate"    # Certificado, diploma, acreditación
    TEST_RESULT = "test_result"    # Resultado de test o análisis

class Evidence(BaseModel):
    """Evidencia vinculada a un control de cumplimiento."""
    __tablename__ = "compliance_evidences"

    id = Column(Integer, primary_key=True)
    control_id = Column(
        Integer,
        ForeignKey("compliance_controls.id"),
        nullable=False
    )
    title = Column(String(300), nullable=False)
    description = Column(Text)
    evidence_type = Column(SAEnum(EvidenceType), nullable=False)
    file_path = Column(String(500))  # Ruta al fichero almacenado
    file_hash = Column(String(128))  # SHA-256 para integridad
    collected_at = Column(DateTime, nullable=False)  # Fecha de recogida
    expires_at = Column(DateTime, nullable=True)  # Fecha de caducidad
    collected_by = Column(String(200))  # Quién recogió la evidencia
    is_valid = Column(Integer, default=1)

    # Relación
    control = relationship("ComplianceControl", back_populates="evidences")
