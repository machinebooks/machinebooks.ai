# Source: The Consultant and the Machine -- Chapter 19
# Pattern: Lessons learned: extraction, patterns, activation
import anthropic
from dataclasses import dataclass, field
from enum import Enum
from datetime import date

class LessonPolarity(Enum):
    POSITIVE = "positive"    # What worked well
    NEGATIVE = "negative"    # What failed or could be improved
    NEUTRAL = "neutral"      # Context change without judgment

class ImpactArea(Enum):
    COST = "cost"
    SCHEDULE = "schedule"
    QUALITY = "quality"
    CLIENT_SATISFACTION = "client_satisfaction"
    TEAM = "team"

@dataclass
class LessonCandidate:
    """Candidate lesson extracted from project documents."""
    summary: str                    # 1-2 sentence summary
    context: str                    # Full situation that originated the lesson
    what_happened: str              # What exactly happened
    root_cause: str                 # Identified root cause (or hypothesis)
    recommendation: str             # What to do differently in the future
    project_type: str               # Project type (audit, migration...)
    project_phase: str              # Phase where it occurred
    category: str                   # Lesson category
    impact_areas: list[ImpactArea]  # Impact areas
    polarity: LessonPolarity        # Positive, negative, or neutral
    confidence: float               # Agent confidence (0.0-1.0)
    source_documents: list[str]     # Source documents
    extraction_date: date = field(default_factory=date.today)

# --- Block 2 ---

EXTRACTION_PROMPT = """Analyze the following documents from a consulting project
and extract candidate lessons learned.

PROJECT CONTEXT:
- Type: {project_type}
- Client: {client_sector}
- Current phase: {current_phase}
- Planned duration: {planned_duration}
- Actual duration to date: {actual_duration}

CRITERIA FOR A VALID LESSON:
1. Must be TRANSFERABLE to future projects (not specific to this client)
2. Must have an identifiable ROOT CAUSE (not just "something went wrong")
3. Must include a CONCRETE RECOMMENDATION (not just "improve communication")
4. Must be VERIFIABLE (based on project facts, not opinions)

NOT lessons:
- One-off observations without pattern ("the client cancelled the Tuesday meeting")
- Personal preferences ("I prefer to do interviews in the morning")
- Problems already known and documented in the current methodology

For each lesson, return a JSON with fields:
summary, context, what_happened, root_cause, recommendation,
project_phase, category, impact_areas, polarity, confidence

DOCUMENTS TO ANALYZE:
{documents}"""


def extract_lessons_from_project(
    project_docs: list[dict],
    project_metadata: dict
) -> list[LessonCandidate]:
    """Extracts candidate lessons from project documents."""
    client = anthropic.Anthropic()

    # Concatenate documents with clear separators
    docs_text = "\n\n---DOCUMENT---\n\n".join(
        f"[{doc['type']}] {doc['title']}\n"
        f"Date: {doc['date']}\n\n{doc['content']}"
        for doc in project_docs
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": EXTRACTION_PROMPT.format(
                project_type=project_metadata["type"],
                client_sector=project_metadata["sector"],
                current_phase=project_metadata["phase"],
                planned_duration=project_metadata["planned_duration"],
                actual_duration=project_metadata["actual_duration"],
                documents=docs_text
            )
        }]
    )

    # Parse JSON response and construct LessonCandidate objects
    raw_lessons = parse_json_response(message.content[0].text)
    return [
        LessonCandidate(
            **lesson,
            project_type=project_metadata["type"],
            source_documents=[d["title"] for d in project_docs]
        )
        for lesson in raw_lessons
        if lesson.get("confidence", 0) >= 0.6  # Confidence threshold
    ]

# --- Block 3 ---

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import anthropic
import hashlib
import json

COLLECTION_NAME = "lessons_learned"

def initialize_lessons_collection(qdrant: QdrantClient):
    """Creates the lessons collection with payload schema."""
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=1024,        # Embedding dimension
            distance=Distance.COSINE
        )
    )

def store_validated_lesson(
    lesson: LessonCandidate,
    qdrant: QdrantClient,
    anthropic_client: anthropic.Anthropic
) -> str:
    """Stores a validated lesson with semantic embedding."""
    # Combined text for embedding: summary + context + recommendation
    embedding_text = (
        f"{lesson.summary}\n"
        f"Context: {lesson.context}\n"
        f"Root cause: {lesson.root_cause}\n"
        f"Recommendation: {lesson.recommendation}"
    )

    # Generate embedding with Voyager model
    embedding_response = anthropic_client.embeddings.create(
        model="voyage-3",
        input=embedding_text
    )
    vector = embedding_response.data[0].embedding

    # Deterministic ID based on content
    lesson_id = hashlib.md5(
        f"{lesson.summary}{lesson.context}".encode()
    ).hexdigest()

    # Payload with metadata for structured filtering
    payload = {
        "summary": lesson.summary,
        "context": lesson.context,
        "what_happened": lesson.what_happened,
        "root_cause": lesson.root_cause,
        "recommendation": lesson.recommendation,
        "project_type": lesson.project_type,
        "project_phase": lesson.project_phase,
        "category": lesson.category,
        "impact_areas": [ia.value for ia in lesson.impact_areas],
        "polarity": lesson.polarity.value,
        "confidence": lesson.confidence,
        "extraction_date": lesson.extraction_date.isoformat(),
        "validation_status": "validated",
        "times_surfaced": 0,
        "times_useful": 0,
        "usefulness_ratio": 0.0
    }

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(
            id=lesson_id,
            vector=vector,
            payload=payload
        )]
    )
    return lesson_id

# --- Block 4 ---

from collections import Counter
from qdrant_client.models import Filter, FieldCondition, MatchValue

PATTERN_DETECTION_PROMPT = """Analyze the following lessons learned
from multiple consulting projects and detect RECURRING PATTERNS.

A valid pattern meets these criteria:
1. Appears in AT LEAST 3 different projects
2. Has a common root cause (not just similar symptoms)
3. Suggests a SYSTEMIC action (not just a one-off fix)

For each pattern, indicate:
- Pattern description
- Number of projects affected
- Common root cause
- Estimated aggregate impact (hours, cost, satisfaction)
- Methodological recommendation: what to change in the practice
- Confidence (high/medium/low)
- Evidence: summaries of the lessons that form the pattern

LESSONS TO ANALYZE ({total_lessons} lessons from {total_projects} projects):
{lessons_text}"""


def detect_patterns(
    qdrant: QdrantClient,
    anthropic_client: anthropic.Anthropic,
    min_lessons: int = 20,
    category_filter: str | None = None
) -> list[dict]:
    """Detects recurring patterns in the lessons corpus."""

    query_filter = Filter(must=[
        FieldCondition(
            key="validation_status",
            match=MatchValue(value="validated")
        )
    ])
    if category_filter:
        query_filter.must.append(
            FieldCondition(
                key="category",
                match=MatchValue(value=category_filter)
            )
        )

    lessons = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=query_filter,
        limit=500,
        with_vectors=False
    )[0]

    if len(lessons) < min_lessons:
        return [{"status": "insufficient_data",
                 "message": f"At least {min_lessons} lessons needed. Currently {len(lessons)}."}]

    project_types = Counter(l.payload["project_type"] for l in lessons)
    categories = Counter(l.payload["category"] for l in lessons)

    lessons_by_category = {}
    for lesson in lessons:
        cat = lesson.payload["category"]
        if cat not in lessons_by_category:
            lessons_by_category[cat] = []
        lessons_by_category[cat].append(lesson.payload)

    lessons_text = ""
    for cat, cat_lessons in lessons_by_category.items():
        lessons_text += f"\n### Category: {cat} ({len(cat_lessons)} lessons)\n"
        for cl in cat_lessons:
            lessons_text += (
                f"- [{cl['polarity']}] {cl['summary']}\n"
                f"  Project type: {cl['project_type']} | Phase: {cl['project_phase']}\n"
                f"  Root cause: {cl['root_cause']}\n"
                f"  Impact: {', '.join(cl['impact_areas'])}\n\n"
            )

    unique_projects = len(set(
        f"{l.payload['project_type']}_{l.payload['extraction_date'][:7]}"
        for l in lessons
    ))

    message = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": PATTERN_DETECTION_PROMPT.format(
                total_lessons=len(lessons),
                total_projects=unique_projects,
                lessons_text=lessons_text
            )
        }]
    )

    return parse_json_response(message.content[0].text)

# --- Block 5 ---

from qdrant_client.models import Filter, FieldCondition, MatchValue

def find_relevant_lessons(
    project_context: dict,
    qdrant: QdrantClient,
    anthropic_client: anthropic.Anthropic,
    top_k: int = 5,
    min_score: float = 0.72
) -> list[dict]:
    """Finds lessons relevant to the current project context."""
    context_text = (
        f"Project of type {project_context['type']} for client in the "
        f"{project_context['sector']} sector. "
        f"Current phase: {project_context['phase']}. "
        f"Current challenge: {project_context.get('current_challenge', '')}. "
        f"Team: {project_context.get('team_size', 'not specified')} people."
    )

    query_embedding = anthropic_client.embeddings.create(
        model="voyage-3", input=context_text
    ).data[0].embedding

    search_filter = Filter(must=[
        FieldCondition(key="validation_status", match=MatchValue(value="validated"))
    ])
    if project_context.get("type"):
        search_filter.must.append(
            FieldCondition(key="project_type", match=MatchValue(value=project_context["type"]))
        )

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=top_k * 2,
        score_threshold=min_score,
        with_payload=True
    )

    relevant_lessons = []
    for result in results[:top_k]:
        lesson = result.payload
        lesson["relevance_score"] = round(result.score, 3)
        lesson["alert_text"] = generate_alert_text(lesson, project_context, anthropic_client)
        relevant_lessons.append(lesson)
        qdrant.set_payload(
            collection_name=COLLECTION_NAME,
            payload={"times_surfaced": lesson["times_surfaced"] + 1},
            points=[result.id]
        )
    return relevant_lessons


def generate_alert_text(lesson: dict, project_context: dict,
                        anthropic_client: anthropic.Anthropic) -> str:
    """Generates contextualized alert text for the team."""
    message = anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Write a brief alert (3-4 sentences) for a consulting
team on a {project_context['type']} project in the {project_context['phase']} phase.

The relevant lesson learned is:
- Summary: {lesson['summary']}
- Original context: {lesson['context']}
- Recommendation: {lesson['recommendation']}

The alert must:
1. Explain WHY it's relevant to their current project
2. Include the concrete recommendation
3. Be direct, without preambles or courtesies"""
        }]
    )
    return message.content[0].text

# --- Block 6 ---

METHODOLOGY_UPDATE_PROMPT = """You are a methodology consultant for a
technology consulting practice. Analyze the following detected patterns
and generate concrete methodological update recommendations.

DETECTED PATTERNS:
{patterns}

CURRENT METHODOLOGY (relevant sections):
{current_methodology}

For each recommendation, indicate:
1. Methodology section affected
2. Proposed change (specific text, not generic)
3. Justification with pattern data
4. Risk of not implementing the change
5. Estimated impact if implemented
6. Priority (high/medium/low)

Do NOT recommend generic changes like "improve communication."
Each change must be a specific instruction implementable without ambiguity."""


def generate_methodology_recommendations(
    patterns: list[dict],
    methodology_sections: dict[str, str],
    anthropic_client: anthropic.Anthropic
) -> list[dict]:
    """Generates methodological update recommendations."""
    relevant_patterns = [
        p for p in patterns
        if p.get("confidence") in ("alta", "media")
        and p.get("affected_projects", 0) >= 3
    ]
    if not relevant_patterns:
        return []

    patterns_text = "\n\n".join(
        f"PATTERN {i+1}: {p['description']}\n"
        f"Projects affected: {p['affected_projects']}\n"
        f"Root cause: {p['root_cause']}\n"
        f"Aggregate impact: {p['aggregated_impact']}\n"
        f"Confidence: {p['confidence']}"
        for i, p in enumerate(relevant_patterns)
    )

    methodology_text = "\n\n".join(
        f"## {section}\n{content}"
        for section, content in methodology_sections.items()
    )

    message = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": METHODOLOGY_UPDATE_PROMPT.format(
                patterns=patterns_text,
                current_methodology=methodology_text
            )
        }]
    )

    recommendations = parse_json_response(message.content[0].text)
    for rec in recommendations:
        rec["generated_date"] = date.today().isoformat()
        rec["source_patterns"] = [p["description"] for p in relevant_patterns]
        rec["status"] = "pending_review"
    return recommendations
