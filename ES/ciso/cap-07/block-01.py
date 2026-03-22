# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
class Asset(BaseModel):
    """Activo de información — entidad central del análisis de riesgos.

    Común a todas las metodologías. El tipo y la valoración
    se interpretan según la methodology del análisis al que pertenece.
    """
    __tablename__ = "risk_assets"

    # --- Identificación ---
    name = Column(String(255), nullable=False)
    code = Column(String(50), comment="Código interno: ACT-001")
    description = Column(Text)
    asset_type = Column(
        SQLEnum(AssetType), nullable=False,
        comment="Tipo de activo — filtrado por methodology"
    )
    owner = Column(String(255), comment="Responsable del activo")

    # --- Clasificación ---
    criticality = Column(
        Integer, default=3,
        comment="Criticidad 1-5, usada para priorización"
    )

    # --- Valoración MAGERIT (dimensiones DICAT) ---
    # Solo se rellenan cuando methodology = MAGERIT_V3
    val_disponibilidad = Column(
        Integer, comment="Disponibilidad 0-4 (MAGERIT)"
    )
    val_integridad = Column(
        Integer, comment="Integridad 0-4 (MAGERIT)"
    )
    val_confidencialidad = Column(
        Integer, comment="Confidencialidad 0-4 (MAGERIT)"
    )
    val_autenticidad = Column(
        Integer, comment="Autenticidad 0-4 (MAGERIT)"
    )
    val_trazabilidad = Column(
        Integer, comment="Trazabilidad 0-4 (MAGERIT)"
    )

    # --- Valoración genérica (ISO 27005, NIST, etc.) ---
    value_qualitative = Column(
        Integer, comment="Valor cualitativo 1-5 (metodologías genéricas)"
    )
    value_quantitative = Column(
        Float, comment="Valor económico en EUR (FAIR, cuantitativas)"
    )

    # --- Metadatos ---
    location = Column(String(255), comment="Ubicación física o lógica")
    classification = Column(
        String(50), comment="Nivel: público, interno, confidencial, secreto"
    )
    dependencies = Column(
        JSON, comment="IDs de activos de los que depende"
    )

    # --- Relaciones ---
    analysis_id = Column(
        BigInteger, ForeignKey("risk_analyses.id"), nullable=False
    )
    risk_scenarios = relationship("RiskScenario", back_populates="asset")
