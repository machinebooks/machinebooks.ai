# Extraído de: LibroPQC/cap-13-rag.md
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.ai_admin import AIRAGCollection, AIRAGDocument

ai_admin_bp = Blueprint('ai_admin', __name__, url_prefix='/api/ai-admin')

@ai_admin_bp.route('/rag/collections', methods=['GET'])
@jwt_required()
def list_collections():
    """Listar todas las colecciones RAG activas"""
    collections = AIRAGCollection.query.order_by(
        AIRAGCollection.name
    ).all()
    return jsonify({
        'success': True,
        'collections': [c.to_dict() for c in collections]
    })

@ai_admin_bp.route('/rag/collections', methods=['POST'])
@jwt_required()
def create_collection():
    """Crear nueva colección con parámetros de chunking"""
    data = request.get_json()
    user_id = get_jwt_identity()
    col = AIRAGCollection(
        name=data['name'],
        description=data.get('description'),
        collection_type=data.get('collection_type', 'custom'),
        embedding_provider_id=data.get('embedding_provider_id'),
        embedding_model=data.get('embedding_model'),
        chunk_size=data.get('chunk_size', 1000),
        chunk_overlap=data.get('chunk_overlap', 200),
        created_by=user_id,
    )
    db.session.add(col)
    db.session.commit()
    return jsonify({
        'success': True,
        'collection': col.to_dict()
    }), 201
