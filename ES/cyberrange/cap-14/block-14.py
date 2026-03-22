# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class Badge(Base):
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(100))
    color = Column(String(7), default='#ffd700')
    difficulty = Column(Enum('beginner', 'intermediate',
                            'advanced', 'expert'),
                       default='intermediate')
    points_reward = Column(Integer, default=100)
    requirements = Column(JSON)    # Requisitos flexibles
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BadgeChallenge(Base):
    """Relación many-to-many: badge requiere N challenges"""
    __tablename__ = "badge_challenges"
    id = Column(Integer, primary_key=True)
    badge_id = Column(Integer, ForeignKey("badges.id",
                                          ondelete="CASCADE"))
    challenge_id = Column(Integer, ForeignKey("challenge.id",
                                              ondelete="CASCADE"))
    is_required = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
