# Extraído de: LibroCyberrange/cap-11-base-datos.md
class Badge(Base):
    """Insignia que se otorga al cumplir criterios."""
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty = Column(Enum('beginner', 'intermediate', 'advanced', 'expert'))
    points_reward = Column(Integer, default=100)
    requirements = Column(JSON)     # Criterios configurables para obtener la insignia
    is_active = Column(Boolean, default=True)

class BadgeChallenge(Base):
    """Relación entre insignias y retos: qué retos hay que completar."""
    __tablename__ = "badge_challenges"
    id = Column(Integer, primary_key=True)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"))
    challenge_id = Column(Integer, ForeignKey("challenge.id", ondelete="CASCADE"))
    is_required = Column(Boolean, default=True)  # Obligatorio u opcional
    order_index = Column(Integer, default=0)      # Orden sugerido
