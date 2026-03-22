# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
def build_team_response(team, db, current_user):
    """Construir respuesta con estadísticas en tiempo real"""
    members = db.query(User).filter(User.team_id == team.id).all()

    team_score = 0
    team_challenges = 0
    member_info = []

    for member in members:
        # Score individual desde ChallengeInstance
        member_score = db.query(
            func.coalesce(func.sum(ChallengeInstance.score), 0)
        ).filter(
            ChallengeInstance.user_id == member.id
        ).scalar() or 0

        member_challenges = db.query(
            func.count(ChallengeInstance.id)
        ).filter(
            ChallengeInstance.user_id == member.id
        ).scalar() or 0

        team_score += member_score
        team_challenges += member_challenges

        member_info.append(TeamMemberInfo(
            id=member.id,
            email=member.email,
            role=member.role,       # red, blue, purple...
            total_score=member_score,
            challenges_completed=member_challenges
        ))

    return TeamResponse(
        id=team.id,
        name=team.name,
        captain_id=team.captain_id,
        max_members=team.max_members,
        current_members=len(members),
        total_score=team_score,
        challenges_completed=team_challenges,
        members=member_info,
        can_delete=(team.created_by == current_user.id
                    and team.captain_id == current_user.id),
        can_transfer_captain=(team.captain_id == current_user.id)
    )
