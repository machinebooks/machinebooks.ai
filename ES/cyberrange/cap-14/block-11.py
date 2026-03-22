# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class Skill(Base):
    """Habilidad técnica rastreable"""
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # offensive, defensive, forensics...
    icon = Column(String(100))
    color = Column(String(7), default='#1e7ce5')
    max_level = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

class SkillLevelConfig(Base):
    """Configuración de niveles por habilidad"""
    __tablename__ = "skill_levels"
    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"))
    level = Column(Integer, nullable=False)
    min_points = Column(Integer, nullable=False)
    max_points = Column(Integer)
    level_name = Column(String(50))   # "Novice", "Practitioner", "Expert"
    color = Column(String(7))
    icon = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class FlagSkill(Base):
    """Vinculación flag → skill (granular)"""
    __tablename__ = "flag_skills"
    id = Column(Integer, primary_key=True)
    flag_id = Column(Integer, ForeignKey("ctf_flag.id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"))
    points_reward = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSkill(Base):
    """Progreso del usuario en una habilidad"""
    __tablename__ = "user_skills"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"))
    current_points = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    total_experience = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow,
                         onupdate=datetime.utcnow)
