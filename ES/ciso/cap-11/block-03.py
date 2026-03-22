# Extraído de: LibroCISO/cap-11-rag-normativo.md
# Ejemplo didáctico: seed del corpus normativo base
NORMATIVE_CORPUS = [
    {
        "title": "RGPD - Reglamento (UE) 2016/679",
        "file": "corpus/rgpd_es.pdf",
        "regulation": "RGPD",
        "authority": "EU",
        "source_url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        "publication_date": "2016-04-27",
        "source_type": "regulation",
    },
    {
        "title": "LOPDGDD - Ley Orgánica 3/2018",
        "file": "corpus/lopdgdd.pdf",
        "regulation": "LOPDGDD",
        "authority": "ES",
        "source_url": "https://www.boe.es/eli/es/lo/2018/12/05/3",
        "publication_date": "2018-12-06",
        "source_type": "regulation",
    },
    {
        "title": "ENS - Real Decreto 311/2022",
        "file": "corpus/ens_rd311_2022.pdf",
        "regulation": "ENS",
        "authority": "CCN",
        "source_url": "https://www.boe.es/eli/es/rd/2022/05/03/311",
        "publication_date": "2022-05-04",
        "source_type": "regulation",
    },
    {
        "title": "AEPD - Guía de Evaluaciones de Impacto",
        "file": "corpus/aepd_guia_eipd.pdf",
        "regulation": "RGPD",
        "authority": "AEPD",
        "source_type": "guide",
    },
    {
        "title": "AEPD - Guía de gestión del riesgo y EIPD",
        "file": "corpus/aepd_gestion_riesgo.pdf",
        "regulation": "RGPD",
        "authority": "AEPD",
        "source_type": "guide",
    },
    {
        "title": "AEPD - Guía de brechas de seguridad",
        "file": "corpus/aepd_brechas.pdf",
        "regulation": "RGPD",
        "authority": "AEPD",
        "source_type": "guide",
    },
    {
        "title": "CCN-STIC 804 - Guía de implantación ENS",
        "file": "corpus/ccn_stic_804.pdf",
        "regulation": "ENS",
        "authority": "CCN",
        "source_type": "guide",
    },
    {
        "title": "CCN-STIC 825 - ENS: Certificaciones 27001",
        "file": "corpus/ccn_stic_825.pdf",
        "regulation": "ENS",
        "authority": "CCN",
        "source_type": "guide",
    },
    {
        "title": "NIS2 - Directiva (UE) 2022/2555",
        "file": "corpus/nis2_es.pdf",
        "regulation": "NIS2",
        "authority": "EU",
        "source_url": "https://eur-lex.europa.eu/eli/dir/2022/2555/oj",
        "publication_date": "2022-12-27",
        "source_type": "regulation",
    },
    {
        "title": "DORA - Reglamento (UE) 2022/2554",
        "file": "corpus/dora_es.pdf",
        "regulation": "DORA",
        "authority": "EU",
        "source_url": "https://eur-lex.europa.eu/eli/reg/2022/2554/oj",
        "publication_date": "2022-12-27",
        "source_type": "regulation",
    },
    {
        "title": "AI Act - Reglamento (UE) 2024/1689",
        "file": "corpus/ai_act_es.pdf",
        "regulation": "AI_ACT",
        "authority": "EU",
        "source_url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "publication_date": "2024-07-12",
        "source_type": "regulation",
    },
]


async def seed_normative_corpus(
    indexer: RAGIndexer,
    db_session,
    collection_name: str = "normative_local",
    embedding_dimensions: int = 768,
):
    """Carga el corpus normativo base. Idempotente: solo indexa lo que falta
    o ha cambiado (detección por hash SHA-256 del fichero)."""

    # 1. Asegurar que la colección existe en Qdrant
    indexer.ensure_collection(collection_name, embedding_dimensions)

    for doc_spec in NORMATIVE_CORPUS:
        file_path = doc_spec["file"]
        current_hash = compute_file_hash(file_path)

        # 2. Verificar si ya está indexado con el mismo hash
        existing = db_session.query(RAGDocument).filter_by(
            title=doc_spec["title"],
            collection_id=collection_id,
        ).first()

        if existing and existing.file_hash == current_hash:
            continue  # Ya indexado, sin cambios → saltar

        if existing and existing.file_hash != current_hash:
            # Documento cambió → eliminar chunks antiguos y re-indexar
            indexer.delete_document_chunks(collection_name, doc_spec["title"])
            existing.status = "processing"

        # 3. Extraer texto y dividir en chunks
        text = extract_text(file_path)
        chunks = chunk_text(text, chunk_size=512, overlap=64)

        # 4. Indexar en Qdrant
        indexed = indexer.index_document(
            collection_name=collection_name,
            chunks=chunks,
            metadata=doc_spec,
        )

        # 5. Registrar en MySQL
        if not existing:
            rag_doc = RAGDocument(
                collection_id=collection_id,
                title=doc_spec["title"],
                source_type=doc_spec["source_type"],
                source_authority=doc_spec.get("authority"),
                source_url=doc_spec.get("source_url"),
                file_path=file_path,
                file_hash=current_hash,
                total_chunks=indexed,
                status="indexed",
            )
            db_session.add(rag_doc)
        else:
            existing.file_hash = current_hash
            existing.total_chunks = indexed
            existing.status = "indexed"

        db_session.commit()
