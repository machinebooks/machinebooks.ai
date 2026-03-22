# Source: The Consultant and the Machine -- Chapter 1
# Pattern: Basic RFP analysis with Claude API, RAG, Agent SDK
import anthropic
from dataclasses import dataclass

@dataclass
class RFPAnalysis:
    """Structured result of an RFP analysis."""
    mandatory_requirements: list[dict]   # Solvency and capability requirements
    evaluation_criteria: list[dict]      # Criteria with weighting
    deadlines: dict                      # Key process dates
    required_profiles: list[dict]        # Required professional profiles
    penalties: list[str]                 # Penalty clauses
    maximum_budget: float | None         # Base budget if stated
    go_nogo_recommendation: str          # "GO", "NO-GO" or "EVALUATE"
    justification: str                   # Reason for the recommendation

client = anthropic.Anthropic(api_key="<YOUR_ANTHROPIC_KEY>")

def analyze_rfp(document_text: str, practice_context: str) -> RFPAnalysis:
    """Analyzes an RFP and extracts key elements for go/no-go decision."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system="""You are a senior technology consulting analyst
specialized in public sector tenders.
Analyze the requirements document and extract the structured
information a pre-sales team needs to decide whether to bid
and, if so, prepare the proposal.

Be exhaustive with mandatory requirements — missing one
means disqualification. Be precise with evaluation criteria
weights. Explicitly state if any data does not appear
in the document.""",
        messages=[{
            "role": "user",
            "content": f"""Analyze this RFP:

--- DOCUMENT ---
{document_text}
--- END DOCUMENT ---

--- PRACTICE CONTEXT ---
{practice_context}
--- END CONTEXT ---

Return the analysis in structured JSON format."""
        }]
    )
    # Parse JSON response to RFPAnalysis
    return parse_analysis(message.content[0].text)

# --- RAG over institutional knowledge (Qdrant) ---

from qdrant_client import QdrantClient, models
import anthropic

# Qdrant client configuration
qdrant = QdrantClient(host="localhost", port=6333)

# Anthropic client configuration for embeddings
anth_client = anthropic.Anthropic(api_key="<YOUR_ANTHROPIC_KEY>")

def index_document(doc_id: str, text: str, metadata: dict):
    """Indexes a practice document in the knowledge base."""

    # Split into ~500-word chunks with overlap
    chunks = split_into_chunks(text, chunk_size=500, overlap=50)

    points = []
    for i, chunk in enumerate(chunks):
        # Generate embedding with Anthropic model
        embedding = generate_embedding(chunk)

        points.append(models.PointStruct(
            id=f"{doc_id}_chunk_{i}",
            vector=embedding,
            payload={
                "text": chunk,
                "doc_id": doc_id,
                "doc_type": metadata.get("type"),     # "proposal", "audit", "lesson"
                "sector": metadata.get("sector"),       # "public", "financial", "industry"
                "framework": metadata.get("framework"), # "ISO27001", "ENS", "DORA"
                "outcome": metadata.get("outcome"),     # "won", "lost", "in_progress"
                "date": metadata.get("date"),
                "chunk_index": i
            }
        ))

    qdrant.upsert(collection_name="consulting_knowledge", points=points)

def search_relevant_experience(query: str, filters: dict = None, limit: int = 10):
    """Searches for relevant prior experience for the current context."""

    query_embedding = generate_embedding(query)

    # Build optional filters
    search_filter = None
    if filters:
        conditions = []
        if "sector" in filters:
            conditions.append(
                models.FieldCondition(
                    key="sector",
                    match=models.MatchValue(value=filters["sector"])
                )
            )
        if "outcome" in filters:
            conditions.append(
                models.FieldCondition(
                    key="outcome",
                    match=models.MatchValue(value=filters["outcome"])
                )
            )
        if conditions:
            search_filter = models.Filter(must=conditions)

    results = qdrant.search(
        collection_name="consulting_knowledge",
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=limit
    )
    return results

# --- Multi-step RFP agent with Claude Agent SDK ---

from claude_code_sdk import Agent, tool

@tool
def search_past_proposals(sector: str, framework: str, limit: int = 5) -> list[dict]:
    """Searches previous proposals in similar sectors and frameworks."""
    results = search_relevant_experience(
        query=f"proposal {sector} {framework}",
        filters={"sector": sector, "outcome": "won"},
        limit=limit
    )
    return [{"text": r.payload["text"], "score": r.score} for r in results]

@tool
def search_lessons_learned(topic: str, limit: int = 5) -> list[dict]:
    """Searches for relevant lessons learned on a topic."""
    results = search_relevant_experience(
        query=topic,
        filters={"doc_type": "lesson"},
        limit=limit
    )
    return [{"text": r.payload["text"], "date": r.payload.get("date")} for r in results]

@tool
def estimate_effort(project_type: str, scope_description: str) -> dict:
    """Estimates effort based on similar historical projects."""
    # Search for similar completed projects
    similar = search_relevant_experience(
        query=f"{project_type}: {scope_description}",
        filters={"doc_type": "completed_project"},
        limit=10
    )
    # Extract effort metrics from similar projects
    efforts = extract_effort_metrics(similar)
    return {
        "average_hours": sum(e["hours"] for e in efforts) / len(efforts),
        "range": [min(e["hours"] for e in efforts), max(e["hours"] for e in efforts)],
        "reference_projects": len(efforts),
        "confidence": "high" if len(efforts) >= 5 else "medium" if len(efforts) >= 3 else "low"
    }

# Configure the agent with available tools
rfp_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[search_past_proposals, search_lessons_learned, estimate_effort],
    system_prompt="""You are a senior consulting analyst. Your job is to:
1. Analyze the provided RFP
2. Search for relevant prior experience in the knowledge base
3. Identify applicable lessons learned
4. Estimate effort based on historical projects
5. Issue a go/no-go recommendation with quantitative justification

Be honest about your analysis confidence. If there is not enough
historical data for a reliable estimate, say so explicitly."""
)
