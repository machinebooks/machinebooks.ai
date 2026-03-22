# Extraído de: LibroCyberrange/cap-12-sistema-ctf.md
class ChallengeMitreTechnique(Base):
    """Vincula un challenge con técnicas MITRE ATT&CK."""
    __tablename__ = 'challenge_mitre_techniques'

    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey('challenge.id', ondelete='CASCADE'))
    technique_id = Column(String(10), ForeignKey('mitre_techniques.technique_id'))
    subtechnique_id = Column(String(15), ForeignKey('mitre_subtechniques.subtechnique_id'))
    skill_level = Column(
        Enum('beginner', 'intermediate', 'advanced'),
        default='beginner'
    )

    # Relaciones
    challenge = relationship("Challenge", back_populates="mitre_techniques")
    technique = relationship("MitreTechnique")
    subtechnique = relationship("MitreSubtechnique")
