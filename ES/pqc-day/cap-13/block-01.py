# Extraído de: LibroPQC/cap-13-rag.md
class AIRAGDocument(db.Model):
    """Documento dentro de una colección RAG"""
    __tablename__ = 'ai_rag_documents'

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(
        db.Integer,
        db.ForeignKey('ai_rag_collections.id'),
        nullable=False
    )
    title = db.Column(db.String(500), nullable=False)
    source_url = db.Column(db.String(1000))       # URL de origen para trazabilidad
    content = db.Column(db.LargeBinary)            # texto comprimido con zlib
    doc_metadata = db.Column(db.JSON)              # versión, emisor, fecha vigencia
    chunk_count = db.Column(db.Integer, default=0) # fragmentos generados
    token_count = db.Column(db.Integer, default=0) # tokens totales del documento
    status = db.Column(
        db.Enum('pending', 'processing', 'indexed', 'failed'),
        default='pending'
    )
    error_message = db.Column(db.Text)             # si status='failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
