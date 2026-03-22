# Source: The Consultant and the Machine -- Chapter 3
# Pattern: Quick estimation, briefing prep, engagement flow
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

def search_knowledge_base(query: str, filters: dict = None) -> list[dict]:
    """Searches the practice RAG for relevant documents.

    In production, this function queries Qdrant with embeddings.
    Here we simplify the interface for didactic clarity.
    """
    # Actual implementation: generates embedding of the query,
    # searches for the K nearest documents in Qdrant,
    # filters by metadata (client, type, date)
    # and returns text + score + metadata
    pass

def get_client_history(client_ref: str) -> dict:
    """Retrieves complete history with a client."""
    results = search_knowledge_base(
        query=f"projects with {client_ref}",
        filters={"type": ["proposal", "report", "lessons_learned"]}
    )
    return {
        "projects": [r for r in results if r["type"] == "project"],
        "deliverables": [r for r in results if r["type"] == "report"],
        "lessons": [r for r in results if r["type"] == "lessons_learned"],
        "last_contact": max(
            (r["date"] for r in results), default=None
        )
    }

BRIEFING_SYSTEM_PROMPT = """You are a technology consulting analyst
who prepares briefings for client meetings.

Your job: given the client context, meeting objective, and
relationship history, generate a structured briefing that
allows the senior consultant to arrive at the meeting prepared
to add value from the first minute.

Rules:
- Be specific, not generic. "The client has concerns about DORA"
  is not useful. "The client must comply with DORA before January 2027
  and their main gap is ICT third-party risk management" is.
- Include questions the client may ask and prepare answers.
- Flag known friction points from previous projects.
- If there is no history, indicate it and suggest discovery questions.
- The tone is internal: direct, without unnecessary diplomacy.
- Maximum 3 pages. The consultant will read it in 10 minutes."""

def prepare_meeting_briefing(
    client_ref: str,
    meeting_objective: str,
    attendees: list[dict],
    additional_context: str = ""
) -> str:
    """Generates a complete briefing for a client meeting."""

    # 1. Retrieve client history
    history = get_client_history(client_ref)

    # 2. Search for regulations relevant to the sector
    regulatory_context = search_knowledge_base(
        query=f"applicable regulation sector {client_ref}",
        filters={"type": ["regulation", "standard"]}
    )

    # 3. Build enriched context for the agent
    context = f"""
CLIENT: {client_ref}
MEETING OBJECTIVE: {meeting_objective}
DATE: {datetime.now().strftime('%Y-%m-%d')}

ATTENDEES:
{json.dumps(attendees, indent=2, ensure_ascii=False)}

CLIENT HISTORY:
- Previous projects: {len(history['projects'])}
- Last contact: {history['last_contact']}
- Relevant lessons learned:
{json.dumps(history['lessons'][:5], indent=2, ensure_ascii=False)}

RELEVANT REGULATORY CONTEXT:
{json.dumps(regulatory_context[:3], indent=2, ensure_ascii=False)}

ADDITIONAL CONTEXT:
{additional_context}
"""

    # 4. Generate briefing with Claude
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=BRIEFING_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Generate the briefing for this meeting:

{context}

Briefing structure:
1. Client context (sector, size, regulation, relationship)
2. Objective and suggested agenda (60 min)
3. Current state: what we know and what we don't
4. Our position and preliminary recommendation
5. Questions we should ask
6. Questions we'll be asked and prepared answers
7. Risks and sensitive topics
8. Suggested next steps"""
        }]
    )

    return message.content[0].text

# --- Quick effort estimation ---

ESTIMATION_SYSTEM_PROMPT = """You are a technology consulting project estimator
with access to historical data from completed projects.

Your job: given a new project, search for the most similar projects
in the historical database, analyze their actual metrics (effort, duration,
team, deviation), and generate a calibrated estimate.

Estimation rules:
- Never give a single number. Give a range with three scenarios:
  optimistic (P25), probable (P50), pessimistic (P75).
- Include the regulatory complexity factor (1.0 to 2.5).
- Include the client maturity factor (1.0 to 1.8):
  client with good documentation = 1.0, client without processes = 1.8.
- List the assumptions conditioning the estimate.
- List the risks that could push the estimate to the pessimistic scenario.
- Show the historical projects used as reference.

IMPORTANT: if there are fewer than 3 comparable projects in the database,
warn about it explicitly. An estimate without a historical base
is an opinion, not an estimate."""

def estimate_project(
    description: str,
    historical_projects: list[dict]
) -> dict:
    """Generates a calibrated estimate based on historical data."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=ESTIMATION_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Estimate this project:

{description}

Comparable historical projects:
{json.dumps(historical_projects, indent=2, ensure_ascii=False)}

Respond in JSON:
{{
  "estimation": {{
    "optimistic_hours": N,
    "probable_hours": N,
    "pessimistic_hours": N,
    "team_size_recommended": N,
    "duration_weeks": {{
      "optimistic": N,
      "probable": N,
      "pessimistic": N
    }}
  }},
  "complexity_factors": {{
    "regulatory": N,
    "client_maturity": N,
    "technical": N
  }},
  "comparable_projects": [
    {{
      "name": "anonymized reference",
      "similarity_score": 0.0-1.0,
      "actual_hours": N,
      "deviation_from_estimate": "N%"
    }}
  ],
  "assumptions": ["..."],
  "risks": ["..."],
  "confidence": "high|medium|low",
  "confidence_justification": "..."
}}"""
        }]
    )
    return json.loads(message.content[0].text)

# --- Integrated flow: from briefing to meeting ---

def prepare_client_engagement(
    client_ref: str,
    opportunity_description: str,
    meeting_date: str,
    attendees: list[dict]
) -> dict:
    """Complete preparation flow for a client engagement."""

    results = {}

    # Step 1: Meeting briefing
    results["briefing"] = prepare_meeting_briefing(
        client_ref=client_ref,
        meeting_objective=f"Explore opportunity: {opportunity_description}",
        attendees=attendees
    )

    # Step 2: Precedent search
    results["precedents"] = search_knowledge_base(
        query=opportunity_description,
        filters={"type": ["project", "proposal"]}
    )

    # Step 3: Preliminary estimation
    historical = [
        p for p in results["precedents"]
        if p.get("type") == "project" and p.get("metrics")
    ]
    if len(historical) >= 2:
        results["estimation"] = estimate_project(
            description=opportunity_description,
            historical_projects=historical
        )
    else:
        results["estimation"] = {
            "warning": "Fewer than 2 comparable projects. "
                       "Estimate not reliable — use expert judgment.",
            "comparable_count": len(historical)
        }

    # Step 4: Pre-meeting checklist
    results["checklist"] = {
        "briefing_reviewed": False,
        "estimation_validated": False,
        "questions_prepared": False,
        "materials_ready": False,
        "internal_alignment": False
    }

    return results
