# Extraído de: LibroPQC/cap-13-rag.md
@ai_admin_bp.route('/rag/collections/<int:col_id>/documents', methods=['POST'])
@jwt_required()
def add_document(col_id):
    """Añadir documento a una colección — inicia pipeline de indexación"""
    col = AIRAGCollection.query.get_or_404(col_id)
    data = request.get_json()

    # Comprimir contenido antes de almacenar
    import zlib
    raw_content = data.get('content', '')
    compressed = zlib.compress(raw_content.encode('utf-8'))

    doc = AIRAGDocument(
        collection_id=col_id,
        title=data['title'],
        source_url=data.get('source_url'),
        content=compressed,
        doc_metadata=data.get('metadata'),
        status='pending',  # El worker lo procesará
    )
    db.session.add(doc)
    col.document_count = col.documents.count() + 1
    db.session.commit()

    # Encolar tarea de fragmentación e indexación
    # from app.tasks import index_rag_document
    # index_rag_document.delay(doc.id)

    return jsonify({
        'success': True,
        'document': doc.to_dict()
    }), 201
