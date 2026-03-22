# Extraído de: LibroTecnico/cap-12-rag-produccion.md
# Ejemplo didáctico: patrones/rag/indexer.py
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import uuid

def index_document_chunks(
    chunks: list,
    document_id: int,
    collection_name: str,
    document_type: str,
    owner_user_id: int,
    allowed_roles: list[str],
    is_current_version: bool,
    qdrant_client,
    embeddings_model,
) -> list[str]:
    """
    Indexa chunks de un documento con metadatos completos para
    recuperación filtrada por usuario, rol y versión activa.
    """
    vectors_ids = []
    texts = [chunk.page_content for chunk in chunks]

    # Generar embeddings en lote para eficiencia
    embeddings = embeddings_model.embed_documents(texts)

    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point_id = str(uuid.uuid4())
        vectors_ids.append(point_id)

        # Los metadatos del payload permiten filtrado sin acceso a la DB
        payload = {
            "document_id": document_id,
            "document_type": document_type,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "text": chunk.page_content,
            "owner_user_id": owner_user_id,
            "allowed_roles": allowed_roles,
            "is_current_version": is_current_version,
            # Metadatos del documento fuente
            "source_page": chunk.metadata.get("page"),
            "ocr_extracted": chunk.metadata.get("ocr", False),
        }

        points.append(PointStruct(
            id=point_id,
            vector=embedding,
            payload=payload,
        ))

    # Inserción en lotes de 100 para eficiencia y control de memoria
    batch_size = 100
    for i in range(0, len(points), batch_size):
        qdrant_client.upsert(
            collection_name=collection_name,
            points=points[i:i + batch_size],
        )

    return vectors_ids


