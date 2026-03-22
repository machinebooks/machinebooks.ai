# Extraído de: LibroCISO/cap-03-ecosistema-tecnico.md
async def seed_regulatory_corpus():
    """Seed automático al primer arranque.
    Carga el corpus normativo base en Qdrant para RAG
    y los catálogos regulatorios en MySQL."""

    # 1. Verificar si ya existe seed previo
    if await check_seed_status():
        logger.info("Corpus normativo ya inicializado — saltando seed")
        return

    # 2. Cargar marcos regulatorios en MySQL
    frameworks = [
        {"code": "RGPD", "version": "2016/679", "articles": 99},
        {"code": "ENS", "version": "RD 311/2022", "controls": 73},
        {"code": "ISO27001", "version": "2022", "controls": 93},
        {"code": "ISO27701", "version": "2019", "controls": 49},
        {"code": "NIS2", "version": "2022/2555", "articles": 46},
        {"code": "DORA", "version": "2022/2554", "articles": 64},
        {"code": "AI_ACT", "version": "2024/1689", "articles": 113},
    ]
    await bulk_insert_frameworks(frameworks)

    # 3. Ingerir documentos en Qdrant para RAG normativo
    corpus_files = [
        "corpus/rgpd_articulos.json",      # 99 artículos chunkeados
        "corpus/ens_medidas.json",          # Anexo II completo
        "corpus/aepd_guias.json",           # Guías prácticas AEPD
        "corpus/ccn_stic_guias.json",       # Guías CCN-STIC relevantes
        "corpus/iso27001_controles.json",   # Controles Anexo A
    ]
    for filepath in corpus_files:
        chunks = load_and_chunk(filepath)
        embeddings = await generate_embeddings(chunks)
        await qdrant_client.upsert(
            collection_name="regulatory_corpus",
            points=embeddings
        )
        logger.info(f"Ingestado {filepath}: {len(chunks)} chunks")

    # 4. Marcar seed como completado
    await mark_seed_complete()
    logger.info("Seed normativo completado — plataforma lista para operar")
