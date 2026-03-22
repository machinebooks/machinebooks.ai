# Extraído de: LibroPQC/cap-13-rag.md
from app.extensions import db
from datetime import datetime

class AIRAGCollection(db.Model):
    """Colección RAG — agrupa documentos por tipo y propósito"""
    __tablename__ = 'ai_rag_collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    # Tipo de colección: qué clase de documentos contiene
    collection_type = db.Column(
        db.Enum('documentation', 'framework', 'policy', 'custom'),
        default='custom'
    )
    # Proveedor de embeddings configurable por colección
    embedding_provider_id = db.Column(
        db.Integer,
        db.ForeignKey('ai_providers.id'),
        nullable=True
    )
    embedding_model = db.Column(db.String(200))
    # Parámetros de fragmentación
    chunk_size = db.Column(db.Integer, default=1000)    # tokens por fragmento
    chunk_overlap = db.Column(db.Integer, default=200)  # tokens de solapamiento
    document_count = db.Column(db.Integer, default=0)   # contador desnormalizado
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    documents = db.relationship(
        'AIRAGDocument', backref='collection',
        lazy='dynamic', cascade='all, delete-orphan'
    )
