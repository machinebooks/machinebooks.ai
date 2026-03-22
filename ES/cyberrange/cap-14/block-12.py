# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
# Dentro de submit_flag(), tras registrar la captura:

# --- Actualizar skills vinculadas a la flag ---
flag_skills = db.query(FlagSkill).filter(
    FlagSkill.flag_id == flag.id
).all()

for fs in flag_skills:
    # Obtener o crear el registro de skill del usuario
    user_skill = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == fs.skill_id
    ).first()

    if not user_skill:
        user_skill = UserSkill(
            user_id=current_user.id,
            skill_id=fs.skill_id,
            current_points=0,
            current_level=1,
            total_experience=0
        )
        db.add(user_skill)
        db.flush()

    # Incrementar puntos
    user_skill.current_points += fs.points_reward
    user_skill.total_experience += fs.points_reward

    # Detectar subida de nivel consultando SkillLevelConfig
    next_level = db.query(SkillLevelConfig).filter(
        SkillLevelConfig.skill_id == fs.skill_id,
        SkillLevelConfig.min_points <= user_skill.current_points
    ).order_by(SkillLevelConfig.level.desc()).first()

    if next_level and next_level.level > user_skill.current_level:
        user_skill.current_level = next_level.level
        # Registrar level-up en el activity log
        db.add(UserActivityLog(
            user_id=current_user.id,
            activity_type='skill_levelup',
            activity_data={
                'skill_id': fs.skill_id,
                'new_level': next_level.level
            },
            points_earned=0,
            created_at=now
        ))
