# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class TeamLeaderboardEntry(BaseModel):
    team_id: int
    team_name: str
    total_score: int
    flags_captured: int
    badges_earned: int
    members_count: int
    challenges_completed: int
    rank: int
    captain_email: Optional[str] = None

@router.get("/team-leaderboard",
            response_model=List[TeamLeaderboardEntry])
def get_team_leaderboard(db: Session = Depends(get_db)):
    """Leaderboard de equipos — agrega scores de miembros"""
    teams = db.query(Team).all()
    team_scores = []

    for team in teams:
        members = db.query(User).filter(
            User.team_id == team.id
        ).all()
        if not members:
            continue

        # Score del equipo: suma de ScoreLog de sus miembros
        team_score = db.query(
            func.coalesce(func.sum(ScoreLog.points), 0)
        ).join(User, ScoreLog.user_id == User.id
        ).filter(User.team_id == team.id).scalar() or 0

        # Challenges completados con case() condicional
        team_challenges = db.query(func.sum(
            case(
                (ChallengeInstance.state == 'done', 1),
                else_=0
            )
        )).join(
            User, ChallengeInstance.user_id == User.id
        ).filter(User.team_id == team.id).scalar() or 0

        team_scores.append({
            'team_id': team.id,
            'team_name': team.name,
            'total_score': int(team_score),
            'members_count': len(members),
            'challenges_completed': int(team_challenges),
            # ... flags_captured, badges_earned análogos
        })

    # Ordenar y asignar ranks
    team_scores = sorted(team_scores,
                        key=lambda x: x['total_score'],
                        reverse=True)
    return [
        TeamLeaderboardEntry(rank=i+1, **data)
        for i, data in enumerate(team_scores)
    ]
