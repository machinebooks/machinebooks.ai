# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class ScoreboardStats(BaseModel):
    total_players: int     # Usuarios que han participado
    total_teams: int       # Equipos con al menos un miembro
    max_score: int         # Puntuación máxima (individual o equipo)
    total_challenges: int  # Challenges disponibles
    total_flags_captured: int  # Total de capturas registradas
