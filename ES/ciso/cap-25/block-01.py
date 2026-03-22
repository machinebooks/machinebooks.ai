# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
class RegulatoryUpdate(BaseModel):
    """Actualización normativa detectada.

    Registra cada publicación relevante con metadatos de
    clasificación, análisis de impacto y marcos afectados.
    """
    __tablename__ = "regulatory_updates"

    source_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("regulatory_sources.id"),
        nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_url: Mapped[str | None] = mapped_column(
        String(2000), nullable=True
    )
    publication_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    effective_date: Mapped[date | None] = mapped_column(
        Date, nullable=True,
        comment="Fecha de entrada en vigor — puede diferir de publicación"
    )
    regulation_type: Mapped[str] = mapped_column(
        Enum(RegulationType), nullable=False,
        default=RegulationType.REGULATION
    )
    sector: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="energy|finance|telecom|health|all"
    )
    status: Mapped[str] = mapped_column(
        Enum(UpdateStatus), nullable=False,
        default=UpdateStatus.NEW
    )
    relevance_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Puntuación de relevancia 0-100"
    )
    # --- Campos de análisis IA ---
    ai_summary: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Resumen generado por LLM"
    )
    ai_impact_analysis: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Análisis de impacto generado por LLM"
    )
    affected_frameworks: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment='["ISO27001", "NIS2", "DORA"]'
    )
    affected_controls: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment='[{"framework": "NIS2", "control_id": "5.1", "impact": "high"}]'
    )
    assigned_to: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )
