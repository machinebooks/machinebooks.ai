# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class UserActivityLog(Base):
    __tablename__ = "user_activity_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id",
                                         ondelete="CASCADE"))
    activity_type = Column(Enum(
        'challenge_started',
        'challenge_completed',
        'flag_captured',
        'badge_earned',
        'skill_levelup'
    ))
    activity_data = Column(JSON)         # Contexto estructurado
    points_earned = Column(Integer, default=0)
    skill_points_earned = Column(JSON)   # Desglose por skill
    created_at = Column(DateTime, default=datetime.utcnow)
