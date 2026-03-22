# Extraído de: LibroCyberrange/cap-11-base-datos.md
class Skill(Base):
    """Habilidad técnica que los participantes pueden desarrollar."""
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # "offensive", "defensive", "forensic"
    max_level = Column(Integer, default=100)

class SkillLevelConfig(Base):
    """Configuración de niveles por habilidad: umbrales de puntos y nombres."""
    __tablename__ = "skill_levels"
    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"))
    level = Column(Integer, nullable=False)
    min_points = Column(Integer, nullable=False)
    max_points = Column(Integer)
    level_name = Column(String(50))       # "Novato", "Intermedio", "Experto"

class UserSkill(Base):
    """Puntuación y nivel actual de un usuario en una habilidad."""
    __tablename__ = "user_skills"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"))
    current_points = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    total_experience = Column(Integer, default=0)
