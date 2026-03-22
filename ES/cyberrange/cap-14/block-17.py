# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK"])

@router.get("/tactics", response_model=List[MitreTacticOut])
async def get_mitre_tactics(db: Session = Depends(get_db)):
    """Obtener todas las tácticas MITRE ATT&CK"""
    return db.query(MitreTactic).all()

@router.get("/techniques", response_model=List[MitreTechniqueOut])
async def get_mitre_techniques(
    tactic_id: Optional[str] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Técnicas MITRE, filtrables por táctica y plataforma"""
    query = db.query(MitreTechnique)
    if tactic_id:
        query = query.join(MitreTactic.techniques).filter(
            MitreTactic.tactic_id == tactic_id
        )
    if platform:
        query = query.filter(
            MitreTechnique.platforms.contains(f'"{platform}"')
        )
    return query.all()

@router.post("/challenges/{challenge_id}/techniques",
             response_model=ChallengeMitreOut)
async def add_mitre_technique_to_challenge(
    challenge_id: int,
    technique_data: ChallengeMitreIn,
    db: Session = Depends(get_db)
):
    """Asociar una técnica MITRE a un challenge"""
    # Verificar existencia del challenge
    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id
    ).first()
    if not challenge:
        raise HTTPException(404, "Challenge not found")

    # Verificar existencia de la técnica
    if technique_data.technique_id:
        technique = db.query(MitreTechnique).filter(
            MitreTechnique.technique_id == technique_data.technique_id
        ).first()
        if not technique:
            raise HTTPException(404, "Technique not found")

    # Verificar subtécnica si se proporciona
    if technique_data.subtechnique_id:
        sub = db.query(MitreSubtechnique).filter(
            MitreSubtechnique.subtechnique_id == \
                technique_data.subtechnique_id
        ).first()
        if not sub:
            raise HTTPException(404, "Subtechnique not found")

    # Crear la relación
    relation = ChallengeMitreTechnique(
        challenge_id=challenge_id,
        technique_id=technique_data.technique_id,
        subtechnique_id=technique_data.subtechnique_id,
        skill_level=technique_data.skill_level
    )
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation
