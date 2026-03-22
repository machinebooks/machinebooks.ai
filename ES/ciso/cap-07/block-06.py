# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
class RiskControl(BaseModel):
    """Control aplicado a un escenario de riesgo.

    Un control reduce la probabilidad, el impacto o ambos.
    La eficacia se valora como porcentaje (0.0 a 1.0).
    """
    __tablename__ = "risk_controls"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    control_type = Column(
        String(30),
        comment="preventivo, detectivo, correctivo, disuasorio"
    )

    # --- Eficacia ---
    effectiveness = Column(
        Float, default=0.5,
        comment="Eficacia estimada 0.0-1.0 (0%=inútil, 1.0=perfecto)"
    )
    implementation_status = Column(
        String(30), default="planned",
        comment="planned, in_progress, implemented, verified"
    )

    # --- Vinculación con marcos de cumplimiento ---
    framework_control_id = Column(
        BigInteger, ForeignKey("compliance_controls.id"),
        nullable=True,
        comment="Vínculo con control de un marco (ENS, ISO 27001)"
    )

    # --- Relaciones ---
    scenario_id = Column(
        BigInteger, ForeignKey("risk_scenarios.id"), nullable=False
    )
    scenario = relationship("RiskScenario", back_populates="controls")


class TreatmentPlan(BaseModel):
    """Plan de tratamiento para un escenario de riesgo.

    Documenta la decisión de tratamiento, el responsable,
    los plazos y el seguimiento. Es el entregable que el
    auditor revisa cuando pregunta: '¿qué hacen con este riesgo?'
    """
    __tablename__ = "risk_treatment_plans"

    # --- Estrategia ---
    strategy = Column(
        SQLEnum(TreatmentStrategy), nullable=False,
        comment="mitigate, transfer, avoid, accept"
    )
    justification = Column(
        Text, nullable=False,
        comment="Justificación de la estrategia elegida"
    )

    # --- Responsabilidad ---
    owner = Column(String(255), nullable=False, comment="Responsable")
    approver = Column(String(255), comment="Quien aprueba la decisión")
    approved_date = Column(DateTime, comment="Fecha de aprobación formal")

    # --- Plazos ---
    target_date = Column(DateTime, comment="Fecha objetivo de implementación")
    review_date = Column(DateTime, comment="Próxima revisión programada")

    # --- Seguimiento ---
    status = Column(
        String(30), default="draft",
        comment="draft, approved, in_progress, completed, overdue"
    )
    progress_notes = Column(Text, comment="Notas de seguimiento")

    # --- Riesgo objetivo ---
    target_residual_risk = Column(
        Integer,
        comment="Riesgo residual objetivo tras completar el plan (1-25)"
    )
    target_residual_ale = Column(
        Float, comment="ALE residual objetivo (FAIR)"
    )

    # --- Relaciones ---
    scenario_id = Column(
        BigInteger, ForeignKey("risk_scenarios.id"),
        nullable=False, unique=True
    )
    scenario = relationship("RiskScenario", back_populates="treatment_plan")
