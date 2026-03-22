# Chapter 12 — PrivacyAgent: GDPR analysis and DPIA generation
#
# The most-used agent in the platform. Generates privacy analyses,
# DPIAs, treatment evaluations, and recommendations for technical
# and organizational measures — all with full tracing.

from datetime import datetime, timezone

try:
    from backend.agents.base import BaseAgent
except ImportError:
    from base import BaseAgent


class PrivacyAgent(BaseAgent):
    """Agent specialized in privacy and data protection.

    Generates GDPR analyses, DPIAs, treatment evaluations,
    and recommendations for technical and organizational measures.

    Tools available to this agent:
    - query_processings: query data processing activities
    - query_dpias: query existing DPIAs
    - query_breaches: query data breach records
    - search_rag: search the regulatory corpus (GDPR, LOPDGDD)
    """

    TOOLS = [
        "query_processings",
        "query_dpias",
        "query_breaches",
        "search_rag",
    ]

    def gather_data(self, params: dict) -> dict:
        """Phase 1: Query treatment data, previous DPIAs, and regulatory context."""
        processing_id = params["processing_id"]

        # Query the data processing activity from the database
        # In production: use self.db_session with proper ORM queries
        processing = self._query_processing(processing_id)
        if not processing:
            raise ValueError(f"Processing activity {processing_id} not found")

        # Query previous DPIAs for context
        previous_dpias = self._query_previous_dpias(processing_id)

        # Query related breaches (inform the risk analysis)
        related_breaches = self._query_related_breaches(processing_id)

        # Search the regulatory corpus via RAG
        rag_context = self._search_rag(
            query=f"DPIA impact assessment treatment "
                  f"{processing.get('name', '')} {processing.get('purpose', '')}",
            collection="rgpd_lopdgdd",
            top_k=8,
        )

        return {
            "processing": processing,
            "previous_dpias": previous_dpias,
            "related_breaches": related_breaches,
            "normative_context": rag_context,
        }

    def analyze(self, gathered: dict, params: dict) -> dict:
        """Phase 2: Analyze the treatment with Claude using GDPR criteria."""
        processing = gathered["processing"]

        system_prompt = (
            "You are a privacy analyst expert in GDPR and national data protection laws. "
            "Analyze the provided data processing activity following the criteria "
            "of the supervisory authority for impact assessments.\n\n"
            "RULES:\n"
            "- Cite specific GDPR articles when applicable\n"
            "- If information is missing, state it explicitly\n"
            "- Do not invent data not present in the context\n"
            "- Assess necessity, proportionality, and risks\n"
            "- Propose concrete technical and organizational measures"
        )

        user_prompt = self._build_analysis_prompt(gathered)

        # Call the LLM with token tracking
        response = self.llm_service.call(
            service_name="privacy_agent",
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
        )

        # Update counters for tracing
        self.total_tokens += response.get("input_tokens", 0) + response.get("output_tokens", 0)
        self.total_cost += response.get("cost_eur", 0.0)

        return {
            "analysis_text": response["content"],
            "model_used": response.get("model", "unknown"),
            "tokens": response.get("input_tokens", 0) + response.get("output_tokens", 0),
            "cost": response.get("cost_eur", 0.0),
        }

    def generate_output(self, analysis: dict, params: dict) -> dict:
        """Phase 3: Generate the formal artifact (privacy analysis report)."""
        return {
            "type": "privacy_analysis",
            "processing_id": params["processing_id"],
            "analysis": analysis["analysis_text"],
            "model_used": analysis["model_used"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tokens_consumed": analysis["tokens"],
            "cost_eur": analysis["cost"],
            "requires_human_review": True,  # Always — AI assists, human decides
        }

    # ── Helper methods (simplified for didactic purposes) ─────────────────

    def _query_processing(self, processing_id: int) -> dict:
        """Query a data processing activity. Placeholder for ORM query."""
        # In production: self.db_session.query(DataProcessingActivity).filter(...)
        return {"id": processing_id, "name": "Example treatment", "purpose": "HR management"}

    def _query_previous_dpias(self, processing_id: int) -> list:
        """Query previous DPIAs for this treatment."""
        return []

    def _query_related_breaches(self, processing_id: int) -> list:
        """Query breaches related to this treatment."""
        return []

    def _search_rag(self, query: str, collection: str, top_k: int) -> list:
        """Search the regulatory corpus via RAG."""
        # In production: call the RAG pipeline service
        return []

    def _build_analysis_prompt(self, gathered: dict) -> str:
        """Build the user prompt with gathered data and normative context."""
        processing = gathered["processing"]
        context = gathered.get("normative_context", [])

        prompt = f"""Analyze this data processing activity:

Name: {processing.get('name', 'N/A')}
Purpose: {processing.get('purpose', 'N/A')}
Legal basis: {processing.get('legal_basis', 'N/A')}
Data categories: {processing.get('personal_data_categories', 'N/A')}
Special categories: {processing.get('special_categories', False)}

Regulatory context from corpus:
"""
        for i, chunk in enumerate(context):
            prompt += f"\n[Source {i+1}]: {chunk.get('text', '')[:500]}"

        prompt += """

Please provide:
1. Assessment of necessity and proportionality
2. Identified risks to data subject rights and freedoms
3. Recommended technical and organizational measures
4. Whether a DPIA is required under Art. 35 GDPR
"""
        return prompt
