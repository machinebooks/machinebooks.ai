# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
@router.post("/", response_model=TeamResponse)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear un nuevo equipo — el creador es automáticamente capitán"""
    # Verificar nombre único
    existing = db.query(Team).filter(Team.name == team_data.name).first()
    if existing:
        raise HTTPException(400, "Ya existe un equipo con ese nombre")

    # Un usuario no puede estar en dos equipos
    if current_user.team_id:
        raise HTTPException(400, "Ya perteneces a un equipo")

    # Crear equipo y asignar capitanía atómicamente
    new_team = Team(
        name=team_data.name,
        description=team_data.description,
        captain_id=current_user.id,
        created_by=current_user.id,
        max_members=team_data.max_members  # Default: 5
    )
    db.add(new_team)
    db.flush()  # Obtener ID antes del commit

    # El creador se une automáticamente
    current_user.team_id = new_team.id
    db.commit()

    return build_team_response(new_team, db, current_user)
