# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class TeamJoinRequest(Base):
    """Solicitudes para unirse a un equipo"""
    __tablename__ = "team_join_request"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    message = Column(Text)          # Mensaje del solicitante
    status = Column(Enum('pending', 'approved', 'rejected', 'cancelled'),
                   default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(Integer, ForeignKey("user.id"))

class TeamInvitation(Base):
    """Invitaciones enviadas por capitanes"""
    __tablename__ = "team_invitation"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    invited_user_id = Column(Integer, ForeignKey("user.id"))
    invited_by = Column(Integer, ForeignKey("user.id"))
    message = Column(Text)
    status = Column(Enum('pending', 'accepted', 'declined', 'expired'),
                   default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
