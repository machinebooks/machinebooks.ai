# Source: The Consultant and the Machine -- Chapter 17
# Pattern: Institutional memory: ingestion, extraction, alerts
# pipeline/ingest.py — Document ingestion pipeline
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import hashlib

@dataclass
class DocumentChunk:
    """Document fragment ready for extraction."""
    doc_id: str
    chunk_index: int
    text: str
    source_file: str
    section_title: str  # Section title from the original document
    project_code: str
    author: str
    created_at: datetime

class DocumentIngester:
    """Ingests documents and produces chunks for extraction."""

    SUPPORTED_FORMATS = {".pdf", ".docx", ".pptx", ".md", ".eml"}
    MAX_CHUNK_WORDS = 800    # Fragments of ~800 words
    OVERLAP_WORDS = 100      # Overlap between fragments

    def __init__(self, extractors: dict, queue):
        self.extractors = extractors  # {".pdf": PdfExtractor, ...}
        self.queue = queue            # Celery queue for async processing

    def ingest(self, file_path: Path, metadata: dict) -> list[DocumentChunk]:
        """Ingests a document and enqueues chunks for extraction."""
        # Verify supported format
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {file_path.suffix}")

        # Verify sharing permissions
        sharing_level = metadata.get("sharing", "personal")
        if sharing_level == "personal":
            return []  # Not ingested without authorization

        # Extract plain text with sections
        extractor = self.extractors[file_path.suffix.lower()]
        sections = extractor.extract_sections(file_path)

        # Generate unique document ID
        doc_id = hashlib.sha256(
            f"{file_path.name}:{metadata['project']}:{metadata['author']}".encode()
        ).hexdigest()[:16]

        # Segment into chunks with overlap
        chunks = self._chunk_sections(sections, doc_id, metadata)

        # Enqueue each chunk for extraction + tagging
        for chunk in chunks:
            self.queue.send_task(
                "extraction.process_chunk",
                args=[chunk],
                queue="knowledge_extraction"
            )

        return chunks

# --- Block 2 ---

# extraction/knowledge_agent.py — Knowledge extraction agent
import anthropic
import json

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

EXTRACTION_PROMPT = """You are a consulting knowledge analyst.
Your task is to extract reusable knowledge fragments from the following text.

For each fragment, identify:
1. TYPE: "decision" | "pattern" | "lesson" | "insight"
2. CONTEXT: situation where it applies (sector, project type, problem)
3. CONTENT: the knowledge itself, formulated to be useful outside
   the original project (without client names or confidential data)
4. RESULT: what consequence it had (if mentioned)
5. CONDITIONS: when it applies and when it does NOT apply

Rules:
- Extract only reusable knowledge, not descriptive summaries
- Anonymize any reference to specific clients or projects
- If the text contains no reusable knowledge, return an empty list
- Maximum 5 fragments per text chunk
- Each fragment must be understandable without the original document

Return JSON with format:
[{"type": "...", "context": "...", "content": "...",
  "result": "...", "conditions": "..."}]"""

def extract_knowledge(chunk_text: str, section_title: str) -> list[dict]:
    """Extracts knowledge fragments from a text chunk."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"## Section: {section_title}\n\n{chunk_text}"
        }],
        system=EXTRACTION_PROMPT,
        temperature=0.1  # Low temperature for deterministic extraction
    )

    try:
        fragments = json.loads(message.content[0].text)
        # Filter empty or low-quality fragments
        return [f for f in fragments if _is_quality_fragment(f)]
    except json.JSONDecodeError:
        return []

def _is_quality_fragment(fragment: dict) -> bool:
    """Validates that a fragment meets minimum quality requirements."""
    required_fields = {"type", "context", "content"}
    if not required_fields.issubset(fragment.keys()):
        return False
    # Content must have substance (more than 30 words)
    if len(fragment["content"].split()) < 30:
        return False
    # Verify no residual sensitive data
    sensitive_patterns = ["@", "http://", "https://", "192.168", "10.0."]
    return not any(p in fragment["content"] for p in sensitive_patterns)

# --- Block 3 ---

# extraction/tagging_agent.py — Automatic tagging agent
import anthropic
import json

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

# Closed taxonomy for sectors and domains, open for technologies
TAXONOMY = {
    "sectors": [
        "publico", "financiero", "industrial",
        "sanitario", "tecnologico", "energia", "retail"
    ],
    "domains": [
        "seguridad", "arquitectura", "datos", "operaciones",
        "cumplimiento", "ia", "cloud", "devops"
    ],
    "project_types": [
        "auditoria", "consultoria", "implantacion",
        "formacion", "preventa", "assessment"
    ],
    "outcomes": ["exito", "parcial", "fallido", "desconocido"]
}

TAGGING_PROMPT = f"""Classify the following knowledge fragment
according to this taxonomy. Assign one or more values per axis.

Taxonomy:
- sector: {TAXONOMY['sectors']}
- domain: {TAXONOMY['domains']}
- project_type: {TAXONOMY['project_types']}
- outcome: {TAXONOMY['outcomes']}
- technologies: [open list — identify technologies mentioned]
- relevance: 1-5 (5 = knowledge reusable in many contexts)

Return strict JSON with these fields."""

def tag_fragment(fragment: dict) -> dict:
    """Tags a knowledge fragment with metadata."""
    message = client.messages.create(
        model="claude-haiku-4-5",  # Haiku for tagging: fast and cheap
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": json.dumps(fragment, ensure_ascii=False)
        }],
        system=TAGGING_PROMPT,
        temperature=0.0
    )

    tags = json.loads(message.content[0].text)

    # Validate against closed taxonomy
    tags["sector"] = [s for s in tags.get("sector", [])
                      if s in TAXONOMY["sectors"]]
    tags["dominio"] = [d for d in tags.get("dominio", [])
                       if d in TAXONOMY["domains"]]

    return {**fragment, "tags": tags}

# --- Block 4 ---

# storage/knowledge_store.py — Vector storage with Qdrant
from qdrant_client import QdrantClient, models
import anthropic
import hashlib

# Local Qdrant connection (data under our control)
qdrant = QdrantClient(host="localhost", port=6333)
claude = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

COLLECTION_NAME = "knowledge_base"

def init_collection():
    """Creates the collection with indexes for metadata filtering."""
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=1024,  # Embedding dimension
            distance=models.Distance.COSINE
        ),
    )

def store_fragment(fragment: dict, embedding: list[float]):
    """Stores a fragment with its embedding and metadata."""
    fragment_id = hashlib.md5(
        fragment["content"].encode()
    ).hexdigest()

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[models.PointStruct(
            id=fragment_id,
            vector=embedding,
            payload={
                "type": fragment["type"],
                "context": fragment["context"],
                "content": fragment["content"],
                "result": fragment.get("result", ""),
                "conditions": fragment.get("conditions", ""),
                "sector": fragment["tags"].get("sector", []),
                "dominio": fragment["tags"].get("dominio", []),
                "tipo_proyecto": fragment["tags"].get("tipo_proyecto", []),
                "tecnologias": fragment["tags"].get("tecnologias", []),
                "resultado": fragment["tags"].get("resultado", "desconocido"),
                "relevancia": fragment["tags"].get("relevancia", 3),
                "doc_id": fragment.get("doc_id", ""),
                "created_at": fragment.get("created_at", ""),
            }
        )]
    )

def search_knowledge(
    query: str,
    query_embedding: list[float],
    filters: dict = None,
    top_k: int = 10
) -> list[dict]:
    """Searches for relevant fragments with optional filters."""
    # Build Qdrant filters
    must_conditions = []
    if filters:
        if "sector" in filters:
            must_conditions.append(
                models.FieldCondition(
                    key="sector",
                    match=models.MatchAny(any=filters["sector"])
                )
            )
        if "dominio" in filters:
            must_conditions.append(
                models.FieldCondition(
                    key="dominio",
                    match=models.MatchAny(any=filters["dominio"])
                )
            )
        if "relevancia_min" in filters:
            must_conditions.append(
                models.FieldCondition(
                    key="relevancia",
                    range=models.Range(gte=filters["relevancia_min"])
                )
            )

    search_filter = models.Filter(must=must_conditions) if must_conditions else None

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=top_k,
        score_threshold=0.65  # Minimum similarity threshold
    )

    return [
        {**hit.payload, "score": hit.score}
        for hit in results
    ]

# --- Block 5 ---

# query/knowledge_search.py — Search interface for consultants
import anthropic
import json

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

QUERY_ANALYSIS_PROMPT = """Analyze the user's query and extract:
1. intent: what they're looking for (precedent, pattern, decision, lesson, technology)
2. filters: implicit filters (sector, domain, project type)
3. refined_query: the query reformulated for semantic search

Return JSON: {"intent": "...", "filters": {...}, "refined_query": "..."}"""

SYNTHESIS_PROMPT = """You are the knowledge assistant of a consulting practice.
The user has made a query and these are the most relevant fragments
from the knowledge base.

Respond helpfully:
- Summarize the most relevant findings
- Indicate which project/context each piece of data comes from
- If there are contradictions between fragments, flag them
- If evidence is scarce, say so explicitly
- Never invent information not in the fragments"""

def search_and_synthesize(user_query: str, project_context: dict = None) -> str:
    """Searches for relevant knowledge and synthesizes a response."""
    # Step 1: Analyze the query to extract implicit filters
    analysis = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        messages=[{"role": "user", "content": user_query}],
        system=QUERY_ANALYSIS_PROMPT,
        temperature=0.0
    )
    parsed = json.loads(analysis.content[0].text)

    # Step 2: Generate embedding for the refined query
    query_embedding = generate_embedding(parsed["refined_query"])

    # Step 3: Search Qdrant with extracted filters
    from storage.knowledge_store import search_knowledge
    results = search_knowledge(
        query=parsed["refined_query"],
        query_embedding=query_embedding,
        filters=parsed.get("filters"),
        top_k=8
    )

    if not results:
        return ("No relevant precedents found in the knowledge "
                "base. Consider consulting directly with "
                "the senior team.")

    # Step 4: Synthesize response with context
    context = "\n\n".join([
        f"**Fragment {i+1}** (type: {r['type']}, "
        f"sector: {r.get('sector', 'N/A')}, "
        f"relevance: {r.get('relevancia', 'N/A')}/5):\n{r['content']}"
        for i, r in enumerate(results)
    ])

    synthesis = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"Query: {user_query}\n\nFragments:\n{context}"
        }],
        system=SYNTHESIS_PROMPT,
        temperature=0.2
    )

    return synthesis.content[0].text

# --- Block 6 ---

# proactive/context_alerts.py — Proactive knowledge alerts
from dataclasses import dataclass

@dataclass
class ProjectContext:
    """Current project context for proactive alerts."""
    sector: str
    dominio: list[str]
    tipo_proyecto: str
    tecnologias: list[str]
    descripcion_breve: str

def generate_proactive_alerts(
    project: ProjectContext,
    knowledge_store,
    max_alerts: int = 5
) -> list[dict]:
    """Generates proactive alerts based on the project context."""
    alerts = []

    # Search for lessons learned in similar projects
    lessons = knowledge_store.search_knowledge(
        query=project.descripcion_breve,
        query_embedding=generate_embedding(project.descripcion_breve),
        filters={
            "sector": [project.sector],
            "dominio": project.dominio,
            "relevancia_min": 4  # Only high-relevance fragments
        },
        top_k=max_alerts
    )

    # Filter by type: prioritize lessons and decisions over insights
    priority_order = {"lesson": 0, "decision": 1, "pattern": 2, "insight": 3}
    lessons.sort(key=lambda x: priority_order.get(x["type"], 99))

    for lesson in lessons[:max_alerts]:
        alerts.append({
            "type": lesson["type"],
            "summary": lesson["content"][:200] + "...",
            "full_content": lesson["content"],
            "relevance_score": lesson["score"],
            "action": _suggest_action(lesson)
        })

    return alerts

def _suggest_action(fragment: dict) -> str:
    """Suggests an action based on the fragment type."""
    actions = {
        "lesson": "Review this lesson before repeating the approach.",
        "decision": "Consider this decision as a precedent.",
        "pattern": "This pattern was observed in similar projects.",
        "insight": "Contextual information that may be relevant."
    }
    return actions.get(fragment["type"], "Relevant fragment found.")
