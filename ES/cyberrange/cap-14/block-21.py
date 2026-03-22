# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
import anthropic

async def generate_competency_report(
    user_id: int,
    db: Session
) -> str:
    """Generar informe de competencias con Claude"""
    # Recopilar datos del participante
    user = db.query(User).filter(User.id == user_id).first()

    skills = db.query(UserSkill).filter(
        UserSkill.user_id == user_id
    ).all()

    badges = db.query(UserBadge).filter(
        UserBadge.user_id == user_id,
        UserBadge.is_completed == True
    ).all()

    # Obtener challenges completados con técnicas MITRE
    completed = db.query(ChallengeInstance).filter(
        ChallengeInstance.user_id == user_id,
        ChallengeInstance.state == 'done'
    ).all()

    mitre_coverage = []
    for inst in completed:
        techniques = db.query(ChallengeMitreTechnique).filter(
            ChallengeMitreTechnique.challenge_id == inst.challenge_id
        ).all()
        for t in techniques:
            mitre_coverage.append({
                'technique': t.technique_id,
                'subtechnique': t.subtechnique_id,
                'skill_level': t.skill_level.value
            })

    # Construir contexto para Claude
    context = {
        'participant': user.email,
        'role': user.role,
        'skills': [
            {'name': s.skill.name, 'level': s.current_level,
             'points': s.current_points}
            for s in skills
        ],
        'badges_earned': [b.badge.name for b in badges],
        'challenges_completed': len(completed),
        'mitre_coverage': mitre_coverage,
        'total_score': sum(inst.score for inst in completed)
    }

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="""Eres un analista de competencias en ciberseguridad.
Genera un informe profesional en español que evalúe el nivel
del participante basándote en sus datos de entrenamiento.
Incluye: resumen ejecutivo, fortalezas, áreas de mejora,
cobertura MITRE ATT&CK y recomendaciones de formación.""",
        messages=[{
            "role": "user",
            "content": f"Datos del participante:\n{json.dumps(context, indent=2)}"
        }]
    )

    return message.content[0].text
