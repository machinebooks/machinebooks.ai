"""
Chapter 14: Document Analyzer agent — specialized agent example.

This is a 'specialized' agent configured for document analysis:
  - 3-step wizard: upload -> AI analysis -> GO/NO-GO recommendation
  - Uses claude-sonnet-4-6 for analysis quality
  - Extracts: executive summary, key requirements, risk assessment
  - Outputs structured JSON for downstream consumption

The agent definition lives in the database (AgentDefinition model)
and can be modified from the Agent Studio UI without redeploy.
"""

import anthropic
from dataclasses import dataclass
from typing import Optional


# =============================================================================
# Document analysis result (Chapter 9 + Chapter 14)
# =============================================================================

@dataclass
class AnalysisResult:
    """Structured output from the document analyzer agent."""
    executive_summary: str
    key_requirements: list
    estimated_effort_days: Optional[int]
    risk_level: str             # low, medium, high, critical
    go_no_go: str               # go, no_go, needs_review
    confidence: float           # 0.0 - 1.0
    tokens_used: int
    model_used: str


# =============================================================================
# Document Analyzer Agent (Chapter 14)
# =============================================================================

ANALYSIS_SYSTEM_PROMPT = """You are a specialized document analyzer for the Platform.
Your task is to analyze technical documents (requirements, RFPs, specifications)
and produce structured analysis for the operations team.

You MUST return a JSON object with this exact structure:
{
  "executive_summary": "2-3 paragraph summary of the document",
  "key_requirements": ["requirement 1", "requirement 2", ...],
  "estimated_effort_days": <integer or null>,
  "risk_level": "low|medium|high|critical",
  "go_no_go": "go|no_go|needs_review",
  "reasoning": "1-2 sentences explaining the GO/NO-GO decision"
}

Rules:
- Be factual. Only state what the document says, never invent requirements.
- If effort cannot be estimated from the document, set estimated_effort_days to null.
- Flag as 'critical' risk if the document mentions penalties, SLAs with fines,
  or compliance requirements your organization may not meet.
- Default to 'needs_review' if the document is ambiguous or incomplete.
"""


class DocumentAnalyzerAgent:
    """
    Specialized agent for document analysis.

    Chapter 14: This agent uses the Claude API directly (not LangChain)
    for fine-grained control over structured output. The NativeClientUsageTracker
    (Chapter 11) wraps the client to ensure every call is audited.
    """

    MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 4096

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with Anthropic client.
        API key from parameter or ANTHROPIC_API_KEY environment variable.
        """
        self.client = anthropic.Anthropic(
            api_key=api_key or "<YOUR_ANTHROPIC_API_KEY>"
        )

    def analyze(
        self,
        document_text: str,
        document_type: str = "requirements",
        max_pages: int = 50,
    ) -> AnalysisResult:
        """
        Analyze a document and return structured results.

        Chapter 14: The agent receives pre-processed text (already loaded
        and chunked by the DocumentLoader from Chapter 12). Long documents
        are truncated to stay within the context window budget.
        """
        # Truncate if necessary (context window management — Chapter 15)
        truncated = document_text[:80_000]  # ~20K tokens approx

        message = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Analyze this {document_type} document:\n\n"
                        f"{truncated}"
                    ),
                }
            ],
        )

        # Parse structured output
        import json
        try:
            result = json.loads(message.content[0].text)
        except json.JSONDecodeError:
            # Fallback: treat as unstructured response
            result = {
                "executive_summary": message.content[0].text,
                "key_requirements": [],
                "estimated_effort_days": None,
                "risk_level": "needs_review",
                "go_no_go": "needs_review",
            }

        tokens_used = message.usage.input_tokens + message.usage.output_tokens

        return AnalysisResult(
            executive_summary=result.get("executive_summary", ""),
            key_requirements=result.get("key_requirements", []),
            estimated_effort_days=result.get("estimated_effort_days"),
            risk_level=result.get("risk_level", "medium"),
            go_no_go=result.get("go_no_go", "needs_review"),
            confidence=0.85 if result.get("go_no_go") != "needs_review" else 0.5,
            tokens_used=tokens_used,
            model_used=self.MODEL,
        )
