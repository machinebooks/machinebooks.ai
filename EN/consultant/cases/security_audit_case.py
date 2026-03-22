# Source: The Consultant and the Machine -- Chapter 26
# Pattern: Security audit: analysis, mapping, findings
from anthropic import Anthropic
import json

client = Anthropic()

SYSTEM_PROMPT = """You are a senior information security auditor
with experience in ISO 27001:2022 and ENS (high category).

Analyze the provided document and identify:
1. ISO 27001:2022 controls (Annex A) the document evidences
2. Compliance level per control: complete, partial, insufficient
3. Detected gaps with specific description
4. Related ENS controls (mapped from ISO 27001)

Respond in structured JSON. Be specific: cite paragraphs from the
document that justify each assessment. If a control has no evidence
in this document, do not include it."""

def analyze_document(doc_text: str, doc_name: str) -> dict:
    """Analyzes a document against ISO 27001 and ENS controls."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Document: {doc_name}\n\n{doc_text}"
        }]
    )
    findings = json.loads(response.content[0].text)
    findings["source_document"] = doc_name
    findings["model"] = response.model
    findings["tokens_used"] = response.usage.input_tokens + response.usage.output_tokens
    return findings

# --- Block 2 ---

from anthropic import Anthropic
from dataclasses import dataclass

client = Anthropic()

@dataclass
class ControlMapping:
    iso_control: str          # e.g., "A.8.1 - User endpoint devices"
    ens_measures: list[str]   # e.g., ["mp.eq.1", "mp.eq.2"]
    status: str               # "compliant", "partial", "non_compliant"
    evidence_refs: list[str]  # supporting documents
    gap_description: str      # identified gap (empty if compliant)
    recommendation: str       # suggested corrective action
    priority: str             # "critical", "high", "medium", "low"

def cross_reference_controls(
    iso_findings: list[dict],
    ens_mapping_table: dict
) -> list[ControlMapping]:
    """Cross-references ISO findings against ENS measures using
    regulatory context loaded in the system prompt."""

    prompt = f"""Based on the provided ISO 27001 audit findings,
    generate the cross-mapping against ENS high category.

    For each ISO control with 'partial' or 'non-compliant' status:
    1. Identify affected ENS measures
    2. Assess whether the ISO gap implies an ENS gap
    3. Prioritize: critical if it affects essential service
       availability, high if it affects personal data
       confidentiality, medium/low otherwise

    ISO findings:
    {json.dumps(iso_findings, ensure_ascii=False, indent=2)}

    ISO-ENS mapping table:
    {json.dumps(ens_mapping_table, ensure_ascii=False, indent=2)}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_control_mappings(response.content[0].text)

# --- Block 3 ---

def generate_finding(
    control_id: str,
    document_evidence: list[dict],
    field_notes: list[str],
    cross_ref: ControlMapping
) -> dict:
    """Generates a complete audit finding for a control."""

    context = f"""Control: {control_id} - {cross_ref.iso_control}

    Documentary evidence:
    {json.dumps(document_evidence, ensure_ascii=False, indent=2)}

    Field notes:
    {chr(10).join(f'- {note}' for note in field_notes)}

    ISO/ENS cross-reference status:
    - Status: {cross_ref.status}
    - Affected ENS measures: {', '.join(cross_ref.ens_measures)}
    - Preliminary gap: {cross_ref.gap_description}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="""Generate a professional audit finding.
        Structure: type (major/minor non-conformity/observation/
        improvement opportunity), factual description, evidence,
        impact on the organization, actionable recommendation,
        suggested implementation timeline.
        Tone: objective, precise, without value judgments.
        Language: formal audit English.""",
        messages=[{"role": "user", "content": context}]
    )
    return parse_finding(response.content[0].text)

# --- Block 4 ---

def capture_lesson(
    project_id: str,
    control_id: str,
    context: str,
    decision: str,
    outcome: str,
    tags: list[str]
) -> None:
    """Captures a lesson learned indexed by context."""
    embedding = generate_embedding(
        f"{context} | {decision} | {outcome}"
    )

    lesson = {
        "project_id": project_id,
        "control_id": control_id,
        "sector": "sector_publico",
        "framework": ["iso27001_2022", "ens_alta"],
        "context": context,
        "decision": decision,
        "outcome": outcome,
        "tags": tags,
        "date": "2025-11-28",
        "consultant": "senior_1"  # anonymized
    }

    qdrant_client.upsert(
        collection_name="lessons_learned",
        points=[{
            "id": generate_uuid(),
            "vector": embedding,
            "payload": lesson
        }]
    )
