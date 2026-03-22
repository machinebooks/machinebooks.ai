# Extraído de: LibroCISO/cap-04-registro-tratamientos.md
# Seed data: catálogos sectoriales de la AEPD (información pública)
# Se precargan como borradores para que el DPO los revise y active

AEPD_MUNICIPAL_CATALOG = [
    {
        "name": "Padrón municipal de habitantes",
        "purposes": ["Gestión del padrón municipal"],
        "legal_basis": "legal_obligation",
        "legal_basis_detail": "Art. 6.1.c RGPD — Ley 7/1985 LBRL Art. 16",
        "data_subject_categories": ["ciudadanos_empadronados"],
        "personal_data_categories": [
            "identificativos", "contacto", "nacionalidad", "estudios"
        ],
        "special_categories": False,
        "retention_period": "Permanente (obligación legal)",
    },
    {
        "name": "Gestión tributaria municipal",
        "purposes": ["Gestión y recaudación de tributos municipales"],
        "legal_basis": "legal_obligation",
        "legal_basis_detail": "Art. 6.1.c RGPD — RDL 2/2004 TRLRHL",
        "data_subject_categories": ["contribuyentes"],
        "personal_data_categories": [
            "identificativos", "contacto", "económico-financieros"
        ],
        "special_categories": False,
        "retention_period": "4 años (prescripción tributaria Art. 66 LGT)",
    },
    {
        "name": "Videovigilancia",
        "purposes": ["Seguridad de personas, bienes e instalaciones"],
        "legal_basis": "public_interest",
        "legal_basis_detail": "Art. 6.1.e RGPD — LO 4/1997 + Instrucción AEPD 1/2006",
        "data_subject_categories": ["personas_captadas_por_camaras"],
        "personal_data_categories": ["imagen"],
        "special_categories": False,
        "retention_period": "Máximo 1 mes (Art. 22.3 LOPDGDD)",
    },
    {
        "name": "Registro de entrada y salida",
        "purposes": ["Gestión documental de entrada y salida"],
        "legal_basis": "legal_obligation",
        "legal_basis_detail": "Art. 6.1.c RGPD — Ley 39/2015 LPACAP Art. 16",
        "data_subject_categories": ["ciudadanos", "representantes"],
        "personal_data_categories": ["identificativos", "contacto"],
        "special_categories": False,
        "retention_period": "Según normativa archivística aplicable",
    },
]


async def seed_sector_catalog(
    corporate_id: int,
    sector: str,
    created_by: int
):
    """Precarga tratamientos tipo del catálogo sectorial AEPD.

    Los tratamientos se crean como borradores (status='draft').
    El DPO debe revisarlos, adaptarlos y activarlos.
    """
    catalog = get_catalog_for_sector(sector)  # municipal, pyme, sanidad...

    created = []
    for template in catalog:
        activity = DataProcessingActivity(
            **template,
            corporate_id=corporate_id,
            created_by=created_by,
            status="draft",  # Siempre borrador — el DPO decide
            code=f"RAT-SEED-{len(created)+1:03d}",
            controller_name="[Pendiente de configurar]",
        )
        db.session.add(activity)
        created.append(activity)

    await db.session.commit()

    return {
        "sector": sector,
        "treatments_created": len(created),
        "status": "draft — requiere revisión del DPO"
    }
