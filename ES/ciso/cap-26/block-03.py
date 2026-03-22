# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
class SecurityCultureScore(BaseModel):
    """Métrica de cultura de seguridad por departamento y periodo."""
    __tablename__ = "pa_security_culture_scores"

    department: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    period: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="Formato: 2026-Q1, 2026-03"
    )
    overall_score: Mapped[float] = mapped_column(
        Float, nullable=False,
        comment="Score global 0-100"
    )
    phishing_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="100 - click_rate (invertido)"
    )
    training_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Tasa de completitud de formación"
    )
    policy_compliance_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Tasa de confirmación de políticas"
    )
    incident_reporting_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Tasa de reporte de incidentes"
    )
    breakdown: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment="Desglose detallado por sub-métrica"
    )
