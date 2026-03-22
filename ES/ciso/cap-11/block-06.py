# Extraído de: LibroCISO/cap-11-rag-normativo.md
# Ejemplo didáctico: endpoint FastAPI de búsqueda RAG normativa
from fastapi import APIRouter, Depends, Query
from app.auth.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/rag", tags=["RAG Normativo"])

@router.get("/search")
async def search_normative(
    query: str = Query(..., min_length=5, max_length=500,
                       description="Pregunta sobre regulación"),
    regulation: str | None = Query(None, description="Filtro: RGPD, ENS, NIS2..."),
    top_k: int = Query(5, ge=1, le=20),
    current_user = Depends(get_current_user),
    _perm = Depends(require_permission("rag:search")),
):
    """Búsqueda semántica sobre corpus normativo.

    Devuelve fragmentos relevantes con puntuación de similitud
    y metadatos de la fuente para verificación."""

    # Seleccionar colección según configuración del tenant
    collection = get_tenant_collection(current_user.corporate_id)

    results = await query_normative_rag(
        query=query,
        search_service=rag_search_service,
        collection_name=collection.name,
        regulation_filter=regulation,
    )

    return {
        "query": query,
        "regulation_filter": regulation,
        "answer": results["answer"],
        "sources": results["sources"],
        "model": results["model"],
        "tokens_used": results["tokens_used"],
    }


@router.post("/documents/ingest")
async def ingest_document(
    file: UploadFile,
    title: str = Form(...),
    regulation: str = Form(...),
    source_type: str = Form(...),  # regulation, guide, standard
    authority: str = Form(None),
    current_user = Depends(get_current_user),
    _perm = Depends(require_permission("rag:admin")),
):
    """Ingestión de nuevo documento normativo. Solo administradores.
    La indexación se ejecuta como tarea asíncrona de Celery."""

    # Guardar fichero y lanzar tarea de indexación
    saved_path = await save_upload(file, "corpus")
    task = celery_app.send_task(
        "tasks.rag.index_document",
        kwargs={
            "file_path": str(saved_path),
            "title": title,
            "regulation": regulation,
            "source_type": source_type,
            "authority": authority,
            "corporate_id": current_user.corporate_id,
        },
    )

    return {
        "status": "processing",
        "task_id": task.id,
        "message": f"Documento '{title}' en cola de indexación.",
    }
