# Source: The Consultant and the Machine -- Chapter 7
# Pattern: MCP server: document repository tools
# mcp-servers/doc-repository/tools.py (simplified fragment)
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
    """Searches for similar documents in the corporate repository."""
    # Generate query embedding
    embedding = claude.embeddings.create(
        model="claude-haiku-4-5",
        input=query
    )
    # Search in Qdrant with document type filter
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
    """Retrieves similar historical projects for estimation."""
    # Filter by sector and service type
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
            f"Project: {r.payload['description']}\n"
            f"Sector: {r.payload['sector']}\n"
            f"Duration: {r.payload['duration_days']} days\n"
            f"Team: {r.payload['team_size']} consultants\n"
            f"Deviation: {r.payload['deviation_pct']}%"
        ))
        for r in results[0]
    ]
