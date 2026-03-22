# Source: The Consultant and the Machine -- Chapter 25
# Pattern: Trust: transparency checker, AI literacy workshops
from anthropic import Anthropic
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class TransparencyStatus(Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"

@dataclass
class TransparencyCheck:
    has_methodology_note: bool
    has_reviewer_attribution: bool
    has_unedited_ai_patterns: bool
    raw_output_sections: list[str]
    status: TransparencyStatus

def audit_deliverable_transparency(
    document_path: str,
    reviewer_name: str
) -> TransparencyCheck:
    """Audits a deliverable for transparency protocol compliance
    before delivery."""

    client = Anthropic()
    content = Path(document_path).read_text(encoding="utf-8")

    # Check 1: methodology note present
    methodology_prompt = f"""Analyze this consulting document.
    Does it contain a methodological note declaring AI tool use?
    Respond only 'yes' or 'no'.

    Document (last 2000 characters):
    {content[-2000:]}"""

    resp_method = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": methodology_prompt}]
    )
    has_note = "yes" in resp_method.content[0].text.lower()

    # Check 2: reviewer attribution
    has_reviewer = reviewer_name.lower() in content.lower()

    # Check 3: unedited output patterns
    pattern_prompt = f"""Analyze this consulting document.
    Identify sections that appear to be direct LLM output
    without significant human editing. Indicators: generic
    phrases without client data, excessively uniform structure,
    absence of context-specific nuances.

    Return a JSON list of suspicious section titles.
    If no suspicious sections, return [].

    Document:
    {content[:8000]}"""

    resp_patterns = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": pattern_prompt}]
    )

    import json
    try:
        raw_sections = json.loads(resp_patterns.content[0].text)
    except json.JSONDecodeError:
        raw_sections = []

    # Determine status
    if not has_note or not has_reviewer:
        status = TransparencyStatus.NON_COMPLIANT
    elif len(raw_sections) > 0:
        status = TransparencyStatus.WARNING
    else:
        status = TransparencyStatus.COMPLIANT

    return TransparencyCheck(
        has_methodology_note=has_note,
        has_reviewer_attribution=has_reviewer,
        has_unedited_ai_patterns=len(raw_sections) > 0,
        raw_output_sections=raw_sections,
        status=status
    )

# --- Block 2 ---

from anthropic import Anthropic
from dataclasses import dataclass

@dataclass
class ClientEducationSession:
    """Structures an AI education session
    adapted to the sector and audience level."""
    client_sector: str
    audience_level: str  # "executive", "technical", "mixed"
    concerns: list[str]  # Concerns expressed by the client

def generate_education_agenda(
    session: ClientEducationSession
) -> dict:
    """Generates personalized agenda for an AI demystification
    session based on the client's context."""

    client = Anthropic()

    prompt = f"""Generate a 90-minute agenda for an
    'AI Demystification for Decision-Makers' session with
    these characteristics:

    Client sector: {session.client_sector}
    Audience: {session.audience_level}
    Expressed concerns: {', '.join(session.concerns)}

    The agenda must include:
    1. What an LLM can and cannot do (15 min)
    2. Practical demonstration adapted to the sector (20 min)
    3. How client data is protected (15 min)
    4. Human oversight: what it means in practice (15 min)
    5. AI opportunities for the organization (15 min)
    6. Open questions (10 min)

    Adapt examples to the {session.client_sector} sector.
    If audience is 'executive', avoid technical jargon.
    Directly address the listed concerns.

    Return the agenda in JSON format with fields:
    title, blocks (list of objects with title, duration,
    key_points, sector_example).
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return {"error": "Unstructured format",
                "raw": response.content[0].text}
