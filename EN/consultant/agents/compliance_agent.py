# Source: The Consultant and the Machine -- Chapter 5
# Pattern: Multi-framework compliance agent with Claude Agent SDK
import json
from pathlib import Path
from claude_agent_sdk import Agent, tool
from dataclasses import dataclass, asdict

@dataclass
class Finding:
    """Structured analysis finding."""
    framework_ref: str      # E.g.: "ISO 27001 A.8.2"
    status: str             # compliant | partial | non_compliant | not_applicable
    evidence: str           # Summary of analyzed evidence
    gap: str                # Detected discrepancy
    risk: str               # critical | high | medium | low
    recommendation: str     # Action to close the gap
    confidence: float       # 0.0 to 1.0

@tool
def query_framework(
    framework: str,
    section: str
) -> dict:
    """Queries a reference framework and returns the requirements
    of a specific section or control.

    Args:
        framework: Framework name (iso27001, ens, dora)
        section: Section or control to query (e.g.: 'A.8.2', '8.1')
    """
    # Loads framework from structured JSON files
    framework_path = Path(f"frameworks/{framework}/{section}.json")
    if not framework_path.exists():
        return {"error": f"Section {section} not found in {framework}"}

    with open(framework_path) as f:
        control = json.load(f)

    return {
        "framework": framework,
        "section": section,
        "title": control["title"],
        "requirements": control["requirements"],
        "guidance": control.get("guidance", ""),
        "related_controls": control.get("related", [])
    }

# --- Block 2 ---

from qdrant_client import QdrantClient
import voyageai

qdrant = QdrantClient(host="localhost", port=6333)
voyage = voyageai.Client(api_key="<YOUR_API_KEY>")

@tool
def search_evidence(
    query: str,
    doc_types: list[str] | None = None,
    max_results: int = 5
) -> list[dict]:
    """Searches the client documentation for evidence relevant
    to a specific control or requirement.

    Args:
        query: Description of the control or requirement to evaluate
        doc_types: Document types to search (policy, procedure,
                   record, report). None searches all.
        max_results: Maximum number of results
    """
    # Generate query embedding
    embedding = voyage.embed(
        texts=[query],
        model="voyage-3"
    ).embeddings[0]

    # Build document type filters
    search_filter = None
    if doc_types:
        search_filter = {
            "must": [{"key": "doc_type", "match": {"any": doc_types}}]
        }

    # Search in the active client's collection
    results = qdrant.search(
        collection_name="client_evidence",
        query_vector=embedding,
        query_filter=search_filter,
        limit=max_results
    )

    return [
        {
            "content": hit.payload["content"],
            "source": hit.payload["source_doc"],
            "doc_type": hit.payload["doc_type"],
            "page": hit.payload.get("page", "N/A"),
            "relevance_score": round(hit.score, 3)
        }
        for hit in results
    ]

# --- Block 3 ---

import sqlite3

@tool
def query_previous_findings(
    client_id: str,
    framework: str | None = None,
    control_ref: str | None = None
) -> list[dict]:
    """Queries findings from previous analyses for a client.
    Useful for identifying recurrences and evaluating evolution.

    Args:
        client_id: Client identifier
        framework: Filter by specific framework
        control_ref: Filter by specific control
    """
    conn = sqlite3.connect("findings.db")
    query = """
        SELECT framework_ref, status, gap, risk,
               recommendation, analysis_date, project
        FROM findings
        WHERE client_id = ?
    """
    params = [client_id]

    if framework:
        query += " AND framework = ?"
        params.append(framework)
    if control_ref:
        query += " AND framework_ref = ?"
        params.append(control_ref)

    query += " ORDER BY analysis_date DESC LIMIT 20"
    cursor = conn.execute(query, params)
    columns = [d[0] for d in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# --- Block 4 ---

from claude_agent_sdk import Agent

SYSTEM_PROMPT = """You are a compliance analysis agent for technology
consulting. Your job is to evaluate an organization's posture against
reference frameworks (ISO 27001, ENS, DORA, NIS2).

ANALYSIS PROCESS:
1. Query the framework to obtain control requirements.
2. Search for evidence in the client documentation.
3. Compare the evidence against the requirement.
4. Produce a structured finding.

CRITICAL RULES:
- If you do not find sufficient evidence, mark confidence < 0.5
  and status as 'partial' or 'non_compliant' with an insufficient
  evidence note. NEVER assume compliance without evidence.
- Each finding must cite the specific documentary source.
- Recommendations must be concrete actions, not generic.
  Bad: "Improve the process." Good: "Document an incident response
  procedure with roles, timelines, and escalation."
- Evaluate each control independently. A compliant control does
  not imply related ones are also compliant.
- If you find previous findings for the same control, reference
  the evolution (improvement, stagnation, regression).
"""

def create_compliance_agent(client_id: str, project_id: str) -> Agent:
    """Creates a compliance analysis agent configured
    for a specific client and project."""
    return Agent(
        model="claude-sonnet-4-6",
        system_prompt=SYSTEM_PROMPT,
        tools=[
            query_framework,
            search_evidence,
            query_previous_findings,
            store_finding
        ],
        # Iteration limit to prevent infinite loops
        max_iterations=50,
        # Metadata for traceability
        metadata={
            "client_id": client_id,
            "project_id": project_id,
            "agent_type": "compliance_analysis"
        }
    )

# --- Block 5 ---

import asyncio

async def run_compliance_analysis(
    client_id: str,
    project_id: str,
    framework: str,
    sections: list[str]
) -> list[dict]:
    """Executes a complete compliance analysis against
    the specified sections of a framework."""

    agent = create_compliance_agent(client_id, project_id)
    all_findings = []

    for section in sections:
        # The agent receives the instruction and decides which tools to use
        result = await agent.run(
            f"Evaluate the client's compliance against section "
            f"'{section}' of framework '{framework}'. "
            f"Query the framework, search for evidence, check previous "
            f"findings if they exist, and produce a structured finding "
            f"for each control in the section."
        )

        # Extract findings from agent result
        findings = extract_findings(result)
        all_findings.extend(findings)

        # Progress log for the consultant
        low_confidence = [f for f in findings if f["confidence"] < 0.5]
        print(
            f"[{section}] {len(findings)} findings | "
            f"{len(low_confidence)} require human review"
        )

    return all_findings

# Execution example
findings = asyncio.run(run_compliance_analysis(
    client_id="CLIENT_FIN_2026",
    project_id="GAP_ENS_Q1",
    framework="ens",
    sections=["op.pl", "op.acc", "op.exp", "op.ext",
              "mp.if", "mp.per", "mp.eq", "mp.com",
              "mp.si", "mp.sw", "mp.info", "mp.s"]
))

# --- Block 6 ---

MAPPING_PROMPT = """You are an agent specialized in mapping controls
between security and compliance frameworks. Your job is to identify
correspondences between controls from different frameworks.

For each pair of controls, classify the relationship as:
- EQUIVALENT: they cover the same requirement with similar scope
- PARTIAL: they overlap but one is broader than the other
- COMPLEMENTARY: they reinforce each other without overlapping
- NO_RELATION: they have no thematic connection

Always include the justification for the classification.
"""

@tool
def get_framework_mapping(
    source_framework: str,
    source_control: str,
    target_framework: str
) -> list[dict]:
    """Gets the mapping of a control from one framework to equivalent
    or related controls in another framework.

    Args:
        source_framework: Source framework (iso27001, ens, dora)
        source_control: Source control (e.g.: 'A.5.1')
        target_framework: Target framework
    """
    conn = sqlite3.connect("framework_mappings.db")
    cursor = conn.execute("""
        SELECT target_control, relationship, justification
        FROM mappings
        WHERE source_framework = ?
          AND source_control = ?
          AND target_framework = ?
    """, (source_framework, source_control, target_framework))

    return [
        {
            "target_control": row[0],
            "relationship": row[1],
            "justification": row[2]
        }
        for row in cursor.fetchall()
    ]

# --- Block 7 ---

@tool
def store_finding(
    framework_ref: str,
    status: str,
    evidence: str,
    gap: str,
    risk: str,
    recommendation: str,
    confidence: float,
    source_docs: list[str] | None = None
) -> dict:
    """Stores an analysis finding in the project database.

    Args:
        framework_ref: Reference to the evaluated control
        status: compliant | partial | non_compliant | not_applicable
        evidence: Summary of analyzed evidence
        gap: Description of the discrepancy
        risk: critical | high | medium | low
        recommendation: Concrete action to close the gap
        confidence: Confidence level (0.0 to 1.0)
        source_docs: List of consulted source documents
    """
    # Field validation
    valid_status = {"compliant", "partial", "non_compliant", "not_applicable"}
    valid_risk = {"critical", "high", "medium", "low"}

    if status not in valid_status:
        return {"error": f"Invalid status: {status}. Use: {valid_status}"}
    if risk not in valid_risk:
        return {"error": f"Invalid risk: {risk}. Use: {valid_risk}"}
    if not 0.0 <= confidence <= 1.0:
        return {"error": "Confidence must be between 0.0 and 1.0"}

    conn = sqlite3.connect("findings.db")
    conn.execute("""
        INSERT INTO findings
        (framework_ref, status, evidence, gap, risk,
         recommendation, confidence, source_docs, analysis_date,
         client_id, project_id, reviewed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, 0)
    """, (
        framework_ref, status, evidence, gap, risk,
        recommendation, confidence,
        json.dumps(source_docs or []),
        # client_id and project_id from agent context
        "CURRENT_CLIENT", "CURRENT_PROJECT"
    ))
    conn.commit()

    return {
        "stored": True,
        "framework_ref": framework_ref,
        "status": status,
        "requires_review": confidence < 0.5
    }

# --- Block 8 ---

async def run_multi_framework_analysis(
    client_id: str,
    project_id: str,
    frameworks: list[str]
) -> dict:
    """Executes compliance analysis against multiple frameworks,
    leveraging cross-framework control mappings to avoid duplication."""

    results = {}
    consolidated_controls = set()

    for framework in frameworks:
        sections = get_all_sections(framework)
        agent = create_compliance_agent(client_id, project_id)

        framework_findings = await agent.run(
            f"Execute complete compliance analysis against "
            f"'{framework}'. Controls already evaluated by "
            f"equivalence with another framework are: "
            f"{list(consolidated_controls)}. For those controls, "
            f"verify that the previous evaluation applies and reference "
            f"it instead of repeating the full analysis."
        )

        # Update consolidated controls with mappings
        findings = extract_findings(framework_findings)
        for f in findings:
            mappings = get_framework_mapping(
                framework, f["framework_ref"], "all"
            )
            for m in mappings:
                if m["relationship"] == "EQUIVALENT":
                    consolidated_controls.add(
                        f"{m['target_framework']}:{m['target_control']}"
                    )

        results[framework] = findings

    return {
        "frameworks_analyzed": frameworks,
        "total_findings": sum(len(f) for f in results.values()),
        "findings_by_framework": {
            k: len(v) for k, v in results.items()
        },
        "controls_consolidated": len(consolidated_controls),
        "results": results
    }
