# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
DEFAULT_SOURCES = [
    {
        "name": "BOE - Boletín Oficial del Estado",
        "source_type": "official_journal",
        "url": "https://boe.es/diario_boe/",
        "country": "ES",
        "check_frequency": "daily",
        "notes": "Leyes, RD, resoluciones de ámbito estatal"
    },
    {
        "name": "DOUE - Diario Oficial de la UE",
        "source_type": "official_journal",
        "url": "https://eur-lex.europa.eu/",
        "country": "EU",
        "check_frequency": "daily",
        "notes": "Reglamentos, directivas y decisiones europeas"
    },
    {
        "name": "AEPD - Agencia Española de Protección de Datos",
        "source_type": "regulator",
        "url": "https://www.aepd.es/",
        "country": "ES",
        "check_frequency": "weekly",
        "notes": "Guías, circulares, resoluciones de privacidad"
    },
    {
        "name": "ENISA - Agencia de Ciberseguridad de la UE",
        "source_type": "regulator",
        "url": "https://www.enisa.europa.eu/",
        "country": "EU",
        "check_frequency": "weekly",
        "notes": "Guías técnicas, informes de amenazas"
    },
    {
        "name": "CCN-CERT - Centro Criptológico Nacional",
        "source_type": "sector_authority",
        "url": "https://www.ccn-cert.cni.es/",
        "country": "ES",
        "check_frequency": "weekly",
        "notes": "Guías CCN-STIC, alertas de seguridad"
    },
]


async def seed_regulatory_sources(
    db: AsyncSession, corporate_id: int, user_id: int
) -> int:
    """Crea fuentes por defecto para un nuevo tenant.

    Retorna el número de fuentes creadas.
    Solo crea las que no existan ya (por nombre).
    """
    svc = RegulatoryWatchService(db, corporate_id)
    existing = await svc.list_sources()
    existing_names = {s["name"] for s in existing}
    created = 0

    for source_data in DEFAULT_SOURCES:
        if source_data["name"] not in existing_names:
            await svc.create_source(source_data, user_id)
            created += 1

    return created
