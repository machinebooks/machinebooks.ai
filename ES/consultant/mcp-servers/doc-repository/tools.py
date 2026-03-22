# Extraído de: LibroConsultor/cap-07-claude-code-consultoria.md
# mcp-servers/doc-repository/tools.py (fragmento simplificado)
from mcp.server import Server
from mcp.types import Tool, TextContent
from qdrant_client import QdrantClient
import anthropic

server = Server("doc-repository")
qdrant = QdrantClient(url="http://localhost:6333")
claude = anthropic.Anthropic()

@server.tool()
async def search_documents(
    query: str,
    doc_type: str = "all",  # proposal, audit, gap-analysis, lesson
    max_results: int = 5
) -> list[TextContent]:
    """Busca documentos similares en el repositorio corporativo."""
    # Genera embedding de la consulta
    embedding = claude.embeddings.create(
        model="claude-haiku-4-5",
        input=query
    )
    # Busca en Qdrant con filtro por tipo de documento
    results = qdrant.search(
        collection_name="corporate-knowledge",
        query_vector=embedding.data[0].embedding,
        query_filter={"doc_type": doc_type} if doc_type != "all" else None,
        limit=max_results
    )
    return [
        TextContent(text=f"[{r.payload['title']}]\n{r.payload['content']}")
        for r in results
    ]

@server.tool()
async def get_project_history(
    sector: str = None,
    service_type: str = None,
    min_similarity: float = 0.7
) -> list[TextContent]:
    """Recupera proyectos históricos similares para estimación."""
    # Filtra por sector y tipo de servicio
    filters = {}
    if sector:
        filters["sector"] = sector
    if service_type:
        filters["service_type"] = service_type
    results = qdrant.scroll(
        collection_name="project-history",
        scroll_filter=filters,
        limit=20
    )
    return [
        TextContent(text=(
            f"Proyecto: {r.payload['description']}\n"
            f"Sector: {r.payload['sector']}\n"
            f"Duración: {r.payload['duration_days']} días\n"
            f"Equipo: {r.payload['team_size']} consultores\n"
            f"Desviación: {r.payload['deviation_pct']}%"
        ))
        for r in results[0]
    ]
