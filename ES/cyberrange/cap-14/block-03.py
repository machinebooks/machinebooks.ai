# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class Team(Base):
    """Equipos de jugadores para competiciones"""
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text)
    captain_id = Column(Integer, ForeignKey("user.id"))
    created_by = Column(Integer, ForeignKey("user.id"))
    max_members = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relaciones
    members = relationship("User", back_populates="team",
                          foreign_keys="User.team_id")
    captain = relationship("User", foreign_keys="Team.captain_id")
    creator = relationship("User", foreign_keys="Team.created_by")
