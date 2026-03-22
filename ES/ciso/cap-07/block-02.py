# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
class RiskScenario(BaseModel):
    """Escenario de riesgo — combinación de activo + amenaza + vulnerabilidad.

    El cálculo de riesgo (inherente y residual) depende de la methodology:
    - Cualitativas (MAGERIT, ISO 27005, NIST...): probabilidad × impacto
    - Cuantitativas (FAIR): LEF × LM → ALE
    """
    __tablename__ = "risk_scenarios"

    # --- Identificación ---
    name = Column(String(255), nullable=False)
    code = Column(String(50), comment="ESC-001")
    description = Column(Text)

    # --- Relaciones con activo y amenaza ---
    asset_id = Column(
        BigInteger, ForeignKey("risk_assets.id"), nullable=False
    )
    threat_id = Column(
        BigInteger, ForeignKey("risk_threats.id"), nullable=False
    )
    vulnerability_description = Column(
        Text, comment="Vulnerabilidad explotada en este escenario"
    )

    # --- Valoración cualitativa (MAGERIT, ISO 27005, NIST, etc.) ---
    probability = Column(
        Integer, comment="Probabilidad 1-5"
    )
    impact = Column(
        Integer, comment="Impacto 1-5 (valor máximo de dimensiones afectadas)"
    )
    inherent_risk = Column(
        Integer, comment="Riesgo inherente = probability × impact (1-25)"
    )

    # --- Impacto por dimensión MAGERIT (DICAT) ---
    impact_disponibilidad = Column(Integer, comment="Impacto en D (0-4)")
    impact_integridad = Column(Integer, comment="Impacto en I (0-4)")
    impact_confidencialidad = Column(Integer, comment="Impacto en C (0-4)")
    impact_autenticidad = Column(Integer, comment="Impacto en A (0-4)")
    impact_trazabilidad = Column(Integer, comment="Impacto en T (0-4)")

    # --- Valoración cuantitativa FAIR ---
    fair_lef = Column(
        Float, comment="Loss Event Frequency — eventos/año"
    )
    fair_lm_primary = Column(
        Float, comment="Primary Loss Magnitude — EUR"
    )
    fair_lm_secondary = Column(
        Float, comment="Secondary Loss Magnitude — EUR"
    )
    fair_ale = Column(
        Float, comment="Annual Loss Expectancy = LEF × (LM_p + LM_s)"
    )

    # --- Riesgo residual (tras controles) ---
    residual_probability = Column(Integer, comment="Probabilidad residual 1-5")
    residual_impact = Column(Integer, comment="Impacto residual 1-5")
    residual_risk = Column(
        Integer,
        comment="Riesgo residual = residual_probability × residual_impact"
    )
    residual_fair_ale = Column(
        Float, comment="ALE residual tras controles — EUR (FAIR)"
    )

    # --- Tratamiento ---
    treatment_strategy = Column(
        SQLEnum(TreatmentStrategy),
        comment="Estrategia: mitigar, transferir, evitar, aceptar"
    )
    treatment_justification = Column(
        Text, comment="Justificación de la estrategia elegida"
    )
    risk_owner = Column(
        String(255), comment="Responsable de la decisión de tratamiento"
    )

    # --- Estado ---
    status = Column(
        String(30), default="identified",
        comment="identified, analyzed, treated, accepted, monitoring"
    )
    review_date = Column(
        DateTime, comment="Próxima fecha de revisión"
    )

    # --- Relaciones ---
    analysis_id = Column(
        BigInteger, ForeignKey("risk_analyses.id"), nullable=False
    )
    asset = relationship("Asset", back_populates="risk_scenarios")
    threat = relationship("Threat")
    controls = relationship(
        "RiskControl", back_populates="scenario",
        cascade="all, delete-orphan"
    )
    treatment_plan = relationship(
        "TreatmentPlan", back_populates="scenario", uselist=False
    )
