# Source: The Consultant and the Machine -- Chapter 4
# Pattern: RAG system: ingestion, chunking, search, answer generation
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from qdrant_client import QdrantClient, models
import voyageai
import anthropic

# Configuration
COLLECTION_NAME = "knowledge_base"
CHUNK_SIZE = 500       # tokens per fragment
CHUNK_OVERLAP = 100    # overlap tokens
EMBEDDING_MODEL = "voyage-3"

voyage = voyageai.Client(api_key="<YOUR_VOYAGE_KEY>")
qdrant = QdrantClient(host="localhost", port=6333)


@dataclass
class DocumentMetadata:
    """Structured metadata for each document."""
    doc_type: str          # proposal, report, methodology, lesson
    sector: str            # public, financial, industrial, technology
    year: int              # document year
    framework: str = ""    # ISO_27001, ENS, DORA, NIS2, AI_Act
    outcome: str = ""      # won, lost, cancelled (proposals only)
    project_id: str = ""   # generic project identifier
    tags: list[str] = field(default_factory=list)

# --- Block 2 ---

def chunk_document(text: str, metadata: DocumentMetadata) -> list[dict]:
    """Fragments a document respecting structure and applying windowing."""
    sections = split_by_headers(text)  # splits by # and ##
    chunks = []

    for section_title, section_text in sections:
        tokens = tokenize(section_text)

        if len(tokens) <= CHUNK_SIZE:
            # Short section: single fragment
            chunks.append({
                "text": f"{section_title}\n\n{section_text}",
                "section": section_title,
                "metadata": metadata.__dict__,
                "doc_hash": hashlib.md5(section_text.encode()).hexdigest()
            })
        else:
            # Long section: sliding window
            for i in range(0, len(tokens), CHUNK_SIZE - CHUNK_OVERLAP):
                window = tokens[i:i + CHUNK_SIZE]
                chunk_text = detokenize(window)
                chunks.append({
                    "text": f"{section_title}\n\n{chunk_text}",
                    "section": section_title,
                    "metadata": metadata.__dict__,
                    "doc_hash": hashlib.md5(
                        chunk_text.encode()
                    ).hexdigest()
                })
    return chunks

# --- Block 3 ---

def create_collection():
    """Creates the collection with indexes for efficient filtering."""
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=1024,           # voyage-3 dimensions
            distance=models.Distance.COSINE
        )
    )
    # Indexes for metadata filtering
    for field_name in ["doc_type", "sector", "year", "framework", "outcome"]:
        qdrant.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=f"metadata.{field_name}",
            field_schema=models.PayloadSchemaType.KEYWORD
            if field_name != "year"
            else models.PayloadSchemaType.INTEGER
        )


def ingest_chunks(chunks: list[dict]) -> int:
    """Indexes fragments in Qdrant, avoiding duplicates."""
    existing_hashes = get_existing_hashes()  # queries Qdrant
    new_chunks = [c for c in chunks if c["doc_hash"] not in existing_hashes]

    if not new_chunks:
        return 0

    # Generate embeddings in batch (max 128 per call)
    texts = [c["text"] for c in new_chunks]
    embeddings = []
    for i in range(0, len(texts), 128):
        batch = texts[i:i + 128]
        result = voyage.embed(batch, model=EMBEDDING_MODEL)
        embeddings.extend(result.embeddings)

    # Insert into Qdrant
    points = [
        models.PointStruct(
            id=idx,
            vector=emb,
            payload={
                "text": chunk["text"],
                "section": chunk["section"],
                "metadata": chunk["metadata"],
                "doc_hash": chunk["doc_hash"]
            }
        )
        for idx, (chunk, emb) in enumerate(
            zip(new_chunks, embeddings), start=get_next_id()
        )
    ]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)

# --- Block 4 ---

client_anthropic = anthropic.Anthropic(api_key="<YOUR_ANTHROPIC_KEY>")


def extract_search_filters(query: str) -> dict:
    """Uses Claude to extract implicit filters from the query."""
    response = client_anthropic.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        system=(
            "Extract search filters from the user query. "
            "Return JSON with optional fields: "
            "doc_type (proposal|report|methodology|lesson), "
            "sector (public|financial|industrial|technology), "
            "year_min (int), year_max (int), "
            "framework (ISO_27001|ENS|DORA|NIS2|AI_Act), "
            "outcome (won|lost|cancelled). "
            "Only include fields that can be inferred from the query."
        ),
        messages=[{"role": "user", "content": query}]
    )
    import json
    try:
        return json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError):
        return {}

# --- Block 5 ---

def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """Semantic search with automatically extracted filters."""
    filters = extract_search_filters(query)

    # Generate query embedding
    query_embedding = voyage.embed(
        [query], model=EMBEDDING_MODEL
    ).embeddings[0]

    # Build Qdrant filters
    must_conditions = []
    for key, value in filters.items():
        if key == "year_min":
            must_conditions.append(
                models.FieldCondition(
                    key="metadata.year",
                    range=models.Range(gte=value)
                )
            )
        elif key == "year_max":
            must_conditions.append(
                models.FieldCondition(
                    key="metadata.year",
                    range=models.Range(lte=value)
                )
            )
        else:
            must_conditions.append(
                models.FieldCondition(
                    key=f"metadata.{key}",
                    match=models.MatchValue(value=value)
                )
            )

    query_filter = (
        models.Filter(must=must_conditions)
        if must_conditions else None
    )

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True
    )
    return [
        {
            "text": hit.payload["text"],
            "score": hit.score,
            "section": hit.payload["section"],
            "metadata": hit.payload["metadata"]
        }
        for hit in results
    ]

# --- Block 6 ---

def answer_query(query: str) -> dict:
    """Complete RAG pipeline: search + generation with sources."""
    results = search_knowledge(query, top_k=5)

    if not results:
        return {
            "answer": "I found no relevant documents for this query.",
            "sources": []
        }

    # Build context with numbered sources
    context_parts = []
    for i, r in enumerate(results, 1):
        meta = r["metadata"]
        source_label = (
            f"[Source {i}: {meta['doc_type']} — {meta['sector']} "
            f"— {meta.get('framework', 'general')} — {meta['year']}]"
        )
        context_parts.append(f"{source_label}\n{r['text']}")

    context = "\n\n---\n\n".join(context_parts)

    response = client_anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=(
            "You are a knowledge assistant for a technology consultancy. "
            "Respond based EXCLUSIVELY on the provided context. "
            "Cite sources using [Source N]. "
            "If the context does not contain sufficient information, say so. "
            "DO NOT invent information that is not in the sources."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Knowledge base context:\n\n{context}\n\n"
                f"---\n\nConsultant's question: {query}"
            )
        }]
    )
    return {
        "answer": response.content[0].text,
        "sources": [
            {
                "doc_type": r["metadata"]["doc_type"],
                "sector": r["metadata"]["sector"],
                "year": r["metadata"]["year"],
                "score": round(r["score"], 3),
                "section": r["section"]
            }
            for r in results
        ]
    }

# --- Block 7 ---

# The consultant asks before preparing a proposal
result = answer_query(
    "What approach did we use in ENS audits for healthcare "
    "sector agencies? What problems did we encounter?"
)

print(result["answer"])
# Expected response (generated by Claude with real context):
# "In healthcare sector ENS audits we identified three recurring
#  patterns [Source 1]: the classification of clinical information
#  systems requires specific analysis due to the nature of health
#  data (high category in confidentiality dimension). The main
#  documented problem [Source 3] was the difficulty of obtaining
#  evidence from electronic health record systems, whose administrators
#  prioritized availability over auditing. In the lesson learned from
#  the 2024 project [Source 4], it is recommended to negotiate access
#  to audit logs during the scoping phase, not during execution."

print(f"\nSources consulted: {len(result['sources'])}")
for s in result["sources"]:
    print(f"  - {s['doc_type']} ({s['sector']}, {s['year']}) "
          f"— score: {s['score']}")

# --- Block 8 ---

def chunk_audit_report(text: str) -> list[dict]:
    """Specialized chunking for audit reports."""
    findings = extract_findings(text)  # detects finding patterns
    chunks = []

    for finding in findings:
        # Each finding includes control, evidence, and recommendation
        chunk_text = (
            f"Control: {finding['control']}\n"
            f"Status: {finding['status']}\n"
            f"Evidence: {finding['evidence']}\n"
            f"Finding: {finding['finding']}\n"
            f"Recommendation: {finding['recommendation']}"
        )
        chunks.append({
            "text": chunk_text,
            "section": f"Finding — {finding['control']}",
            "chunk_type": "audit_finding"
        })

    return chunks

# --- Block 9 ---

LESSON_SCHEMA = {
    "project_type": str,       # audit, consulting, assessment
    "sector": str,             # public, financial, industrial
    "phase": str,              # scoping, execution, delivery, closure
    "problem": str,            # what went wrong or what was learned
    "root_cause": str,         # why it happened
    "corrective_action": str,  # what was done
    "recommendation": str,     # what to do in the future
    "impact": str,             # high, medium, low
    "date": str                # YYYY-MM
}

# --- Block 10 ---

def evaluate_retrieval(test_queries: list[dict]) -> dict:
    """Evaluates retrieval quality against ground truth."""
    recalls = []
    filter_accuracies = []
    empty_count = 0

    for test in test_queries:
        query = test["query"]
        relevant_docs = set(test["relevant_doc_hashes"])

        results = search_knowledge(query, top_k=5)

        if not results:
            empty_count += 1
            recalls.append(0.0)
            continue

        # Recall@5
        retrieved_hashes = {
            r.get("doc_hash") for r in results if r.get("doc_hash")
        }
        recall = len(retrieved_hashes & relevant_docs) / len(relevant_docs)
        recalls.append(recall)

        # Filter precision
        expected_filters = test.get("expected_filters", {})
        if expected_filters:
            correct = sum(
                1 for r in results
                if all(
                    r["metadata"].get(k) == v
                    for k, v in expected_filters.items()
                )
            )
            filter_accuracies.append(correct / len(results))

    return {
        "mean_recall_at_5": sum(recalls) / len(recalls),
        "mean_filter_precision": (
            sum(filter_accuracies) / len(filter_accuracies)
            if filter_accuracies else None
        ),
        "empty_rate": empty_count / len(test_queries),
        "total_queries": len(test_queries)
    }
