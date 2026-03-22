# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
class PhishingSimulation(BaseModel):
    """Simulación de phishing con métricas agregadas."""
    __tablename__ = "pa_phishing_simulations"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    template_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="credential_harvest, malware_link, attachment, mfa_fatigue"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="planned"
    )
    # --- Métricas de ejecución ---
    emails_sent: Mapped[int] = mapped_column(Integer, default=0)
    emails_opened: Mapped[int] = mapped_column(Integer, default=0)
    links_clicked: Mapped[int] = mapped_column(Integer, default=0)
    credentials_submitted: Mapped[int] = mapped_column(Integer, default=0)
    reported_by_users: Mapped[int] = mapped_column(Integer, default=0)
    # --- Tasas calculadas ---
    click_rate: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="links_clicked / emails_sent * 100"
    )
    report_rate: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="reported_by_users / emails_sent * 100"
    )
    target_departments: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    ai_adaptive: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="IA adapta dificultad al perfil del departamento"
    )
