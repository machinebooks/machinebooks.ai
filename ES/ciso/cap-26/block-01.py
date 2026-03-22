# Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
class CampaignType(str, enum.Enum):
    ELEARNING = "elearning"
    WORKSHOP = "workshop"
    VIDEO = "video"
    QUIZ = "quiz"
    PHISHING = "phishing"
    NEWSLETTER = "newsletter"


class AwarenessCampaign(BaseModel):
    """Campaña de formación/concienciación en ciberseguridad."""
    __tablename__ = "pa_awareness_campaigns"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    campaign_type: Mapped[str] = mapped_column(
        Enum(CampaignType), nullable=False,
        default=CampaignType.ELEARNING
    )
    status: Mapped[str] = mapped_column(
        Enum(CampaignStatus), nullable=False,
        default=CampaignStatus.PLANNED
    )
    target_audience: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment='["all_employees", "IT", "management"]'
    )
    target_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="Número de destinatarios objetivo"
    )
    completed_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    pass_rate: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Tasa de aprobados 0-100"
    )
    ai_personalized: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="Contenido adaptado por IA al perfil del empleado"
    )
