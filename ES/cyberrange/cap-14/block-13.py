# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class ChallengeSkill(Base):
    """Vinculación challenge completo → skill (bonus por completación)"""
    __tablename__ = "challenge_skills"
    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenge.id",
                                              ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.id",
                                          ondelete="CASCADE"))
    points_reward = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
