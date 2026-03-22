# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
@router.get("/search")
async def search_mitre(
    q: str,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Buscar en tácticas, técnicas y subtécnicas MITRE"""
    results = {"tactics": [], "techniques": [], "subtechniques": []}

    if not type or type == "tactic":
        results["tactics"] = db.query(MitreTactic).filter(
            MitreTactic.name.ilike(f"%{q}%") |
            MitreTactic.description.ilike(f"%{q}%")
        ).limit(10).all()

    if not type or type == "technique":
        results["techniques"] = db.query(MitreTechnique).filter(
            MitreTechnique.name.ilike(f"%{q}%") |
            MitreTechnique.description.ilike(f"%{q}%")
        ).limit(10).all()

    if not type or type == "subtechnique":
        results["subtechniques"] = db.query(MitreSubtechnique).filter(
            MitreSubtechnique.name.ilike(f"%{q}%") |
            MitreSubtechnique.description.ilike(f"%{q}%")
        ).limit(10).all()

    return results
