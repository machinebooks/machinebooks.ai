# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
def _check_badges(db, user, challenge_id, now):
    """Verificar y otorgar badges tras completar un challenge"""
    # Buscar badges que requieran este challenge
    badge_links = db.query(BadgeChallenge).filter(
        BadgeChallenge.challenge_id == challenge_id,
        BadgeChallenge.is_required == True
    ).all()

    for link in badge_links:
        badge = db.get(Badge, link.badge_id)
        if not badge or not badge.is_active:
            continue

        # ¿Ya tiene el badge completo?
        user_badge = db.query(UserBadge).filter(
            UserBadge.user_id == user.id,
            UserBadge.badge_id == badge.id
        ).first()
        if user_badge and user_badge.is_completed:
            continue

        # Contar challenges requeridos vs completados
        required = db.query(BadgeChallenge).filter(
            BadgeChallenge.badge_id == badge.id,
            BadgeChallenge.is_required == True
        ).all()
        required_ids = [bc.challenge_id for bc in required]

        completed = db.query(ChallengeInstance).filter(
            ChallengeInstance.user_id == user.id,
            ChallengeInstance.challenge_id.in_(required_ids),
            ChallengeInstance.state == 'done'
        ).count()

        progress = int((completed / len(required_ids)) * 100) \
                   if required_ids else 0

        # Crear o actualizar progreso
        if not user_badge:
            user_badge = UserBadge(
                user_id=user.id,
                badge_id=badge.id,
                progress_percentage=progress,
                is_completed=False
            )
            db.add(user_badge)
            db.flush()

        user_badge.progress_percentage = progress

        # ¿Completó todos los requeridos?
        if completed >= len(required_ids):
            user_badge.is_completed = True
            user_badge.earned_at = now

            # Bonus de puntos por obtener el badge
            if badge.points_reward and badge.points_reward > 0:
                db.add(ScoreLog(
                    user_id=user.id,
                    points=badge.points_reward,
                    reason=f"Badge obtenido: {badge.name}",
                    ts=now
                ))

            # Activity log para trazabilidad
            db.add(UserActivityLog(
                user_id=user.id,
                activity_type='badge_earned',
                activity_data={
                    'badge_id': badge.id,
                    'badge_name': badge.name
                },
                points_earned=badge.points_reward or 0,
                created_at=now
            ))
