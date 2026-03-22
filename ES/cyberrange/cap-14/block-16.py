# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class ChallengeMitreTechnique(Base):
    """Mapeo challenge → técnica MITRE ATT&CK"""
    __tablename__ = 'challenge_mitre_techniques'
    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer,
                         ForeignKey('challenge.id', ondelete='CASCADE'))
    technique_id = Column(String(10),
                         ForeignKey('mitre_techniques.technique_id'),
                         nullable=True)
    subtechnique_id = Column(String(15),
                            ForeignKey('mitre_subtechniques.subtechnique_id'),
                            nullable=True)
    skill_level = Column(Enum(SkillLevel), default=SkillLevel.beginner)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones ORM para carga eficiente
    technique = relationship("MitreTechnique",
                           back_populates="challenges")
    subtechnique = relationship("MitreSubtechnique",
                              back_populates="challenges")
