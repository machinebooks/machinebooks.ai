# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    total_score: int
    flags_captured: int
    challenges_completed: int
    badges_earned: int
    rank: int
    team_name: Optional[str] = None

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    """Leaderboard individual — score calculado desde ScoreLog"""
    users = db.query(User).all()
    leaderboard = []

    for user in users:
        # Fuente de verdad: ScoreLog
        total_score = db.query(
            func.coalesce(func.sum(ScoreLog.points), 0)
        ).filter(ScoreLog.user_id == user.id).scalar() or 0

        flags_captured = db.query(
            func.count(CtfCapture.id)
        ).filter(CtfCapture.user_id == user.id).scalar() or 0

        challenges_completed = db.query(
            func.count(ChallengeInstance.id)
        ).filter(
            ChallengeInstance.user_id == user.id,
            ChallengeInstance.state == 'done'
        ).scalar() or 0

        badges_earned = db.query(
            func.count(UserBadge.id)
        ).filter(
            UserBadge.user_id == user.id,
            UserBadge.is_completed == True
        ).scalar() or 0

        # Incluir equipo si tiene uno
        team_name = None
        if user.team_id:
            team = db.query(Team).filter(
                Team.id == user.team_id
            ).first()
            team_name = team.name if team else None

        leaderboard.append({
            'user_id': user.id,
            'username': user.email,
            'total_score': int(total_score),
            'flags_captured': int(flags_captured),
            'challenges_completed': int(challenges_completed),
            'badges_earned': int(badges_earned),
            'team_name': team_name
        })

    # Ordenar por score descendente y asignar ranks
    leaderboard = sorted(leaderboard,
                        key=lambda x: x['total_score'],
                        reverse=True)

    return [
        LeaderboardEntry(rank=i+1, **data)
        for i, data in enumerate(leaderboard)
    ]
