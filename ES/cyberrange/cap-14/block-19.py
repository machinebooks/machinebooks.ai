# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
# En get_challenge_detail(), construir lista de técnicas MITRE
mitre_techniques_query = db.query(ChallengeMitreTechnique).filter(
    ChallengeMitreTechnique.challenge_id == challenge_id
).all()

mitre_techniques = []
for mt in mitre_techniques_query:
    if mt.technique_id:
        technique = db.query(MitreTechnique).filter(
            MitreTechnique.technique_id == mt.technique_id
        ).first()
        if technique:
            mitre_techniques.append(MitreTechniqueInfo(
                technique_id=technique.technique_id,
                name=technique.name,
                description=technique.description,
                url=technique.url  # Link a MITRE website
            ))

    if mt.subtechnique_id:
        sub = db.query(MitreSubtechnique).filter(
            MitreSubtechnique.subtechnique_id == mt.subtechnique_id
        ).first()
        if sub:
            mitre_techniques.append(MitreTechniqueInfo(
                technique_id=sub.subtechnique_id,
                name=sub.name,
                description=sub.description,
                url=sub.url
            ))
