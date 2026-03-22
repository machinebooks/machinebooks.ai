# Chapter 13 — CopilotOrchestrator: the CISO's copilot
#
# Three execution modes:
# - CHAT_RAG: direct response with regulatory context from Qdrant
# - AGENT_TOOLS: single agent with database tools
# - ORCHESTRATE: multi-agent coordination (e.g., DPIA = privacy + risk + compliance + report)
#
# Guardrails run BEFORE any LLM processing: length, prompt injection, PII scan.
# Intent classification: heuristics first (70-80%), LLM fallback for ambiguous messages.

import re
import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional


# ── Data classes ──────────────────────────────────────────────────────────

class CopilotMode(str, Enum):
    """Three execution modes of the copilot."""
    CHAT_RAG = "chat_rag"
    AGENT_TOOLS = "agent_tools"
    ORCHESTRATE = "orchestrate"


@dataclass
class CopilotRequest:
    """User input already validated by guardrails."""
    message: str
    session_id: str
    user_id: str
    module_context: str     # Active GRC module (privacy, risk, compliance...)
    tenant_id: str          # Multi-tenancy (mandatory)
    mode_override: Optional[CopilotMode] = None


@dataclass
class OrchestratorStep:
    """An individual step within an orchestrated execution."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_name: str = ""
    action: str = ""
    input_summary: str = ""
    output_summary: str = ""
    tokens_used: int = 0
    cost_eur: float = 0.0
    duration_ms: int = 0
    status: str = "pending"  # pending | running | completed | failed


# ── Intent Classifier ─────────────────────────────────────────────────────

# Patterns indicating agent tasks (action verbs + domain)
AGENT_PATTERNS = [
    (r"\b(generate|prepare|create|draft|write)\b.*\b(report|document|assessment)\b", "report_writer"),
    (r"\b(analyze|evaluate|review|assess)\b.*\b(risk|threat|vulnerability)\b", "risk"),
    (r"\b(analyze|evaluate|review)\b.*\b(treatment|personal data|privacy)\b", "privacy"),
    (r"\b(verify|check|audit)\b.*\b(compliance|control|framework|ENS|ISO)\b", "compliance"),
    (r"\b(import|load|process)\b.*\b(document|file|CSV|Excel)\b", "data_import"),
]

# Patterns indicating multi-agent orchestration
ORCHESTRATION_PATTERNS = [
    r"\b(DPIA|impact assessment)\b",
    r"\b(complete analysis|comprehensive report|global evaluation)\b",
    r"\b(treatment plan)\b.*\b(risk)\b",
    r"\b(audit|gap analysis)\b.*\b(complete|comprehensive)\b",
]


class IntentClassifier:
    """Hybrid classifier: heuristics first, LLM fallback for ambiguous cases.

    Covers 70-80% of messages with deterministic rules.
    The remaining 20-30% use claude-haiku-4-5 (~0.0003 EUR per classification).
    """

    def classify(self, message: str, module_context: str) -> CopilotMode:
        msg_lower = message.lower().strip()

        # Step 1: Multi-agent orchestration?
        for pattern in ORCHESTRATION_PATTERNS:
            if re.search(pattern, msg_lower):
                return CopilotMode.ORCHESTRATE

        # Step 2: Single agent task?
        for pattern, agent_key in AGENT_PATTERNS:
            if re.search(pattern, msg_lower):
                return CopilotMode.AGENT_TOOLS

        # Step 3: Informational question? (no action verbs)
        if msg_lower.startswith(("what", "which", "how", "why", "where",
                                  "when", "explain", "describe", "define")):
            return CopilotMode.CHAT_RAG

        # Step 4: Default to CHAT_RAG (safest and cheapest mode)
        # In production: call claude-haiku-4-5 as classification fallback
        return CopilotMode.CHAT_RAG


# ── Orchestrator ──────────────────────────────────────────────────────────

class CopilotOrchestrator:
    """Central orchestrator for the CISO copilot.

    Classifies intent, applies guardrails, and delegates to
    one of three modes. Every step is logged to audit_trail.

    Usage:
        orchestrator = CopilotOrchestrator(llm_factory, rag_service, agent_registry, guardrails)
        async for event in orchestrator.process(request):
            send_sse_event(event)
    """

    def __init__(self, llm_factory, rag_service, agent_registry, guardrails):
        self.llm_factory = llm_factory
        self.rag_service = rag_service
        self.agent_registry = agent_registry
        self.guardrails = guardrails
        self.intent_classifier = IntentClassifier()

    async def process(self, request: CopilotRequest) -> AsyncGenerator[dict, None]:
        """Main entry point. Returns an async generator of SSE events."""
        execution_id = str(uuid.uuid4())
        start_time = time.monotonic()

        # 1. Input guardrails (block if risk detected)
        guard_result = await self.guardrails.scan(request.message)
        if not guard_result.passed:
            yield {
                "type": "error",
                "code": guard_result.violation_code,
                "message": guard_result.user_message,
            }
            await self._log_blocked_request(request, guard_result, execution_id)
            return

        # 2. Classify intent -> execution mode
        mode = request.mode_override or self.intent_classifier.classify(
            message=request.message,
            module_context=request.module_context,
        )
        yield {"type": "mode_selected", "mode": mode.value}

        # 3. Delegate to the corresponding mode
        if mode == CopilotMode.CHAT_RAG:
            async for event in self._execute_chat_rag(request, execution_id):
                yield event

        elif mode == CopilotMode.AGENT_TOOLS:
            async for event in self._execute_agent(request, execution_id):
                yield event

        elif mode == CopilotMode.ORCHESTRATE:
            async for event in self._execute_orchestration(request, execution_id):
                yield event

        # 4. Log complete execution in audit_trail
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        yield {"type": "completed", "execution_id": execution_id, "duration_ms": elapsed_ms}

    # ── Mode implementations (simplified) ─────────────────────────────────

    async def _execute_chat_rag(self, request: CopilotRequest,
                                execution_id: str) -> AsyncGenerator[dict, None]:
        """CHAT_RAG: semantic search + LLM response with cited sources."""
        yield {"type": "agent_started", "agent": "rag_search", "action": "Searching regulatory corpus"}

        # Search Qdrant for relevant regulatory fragments
        results = self.rag_service.search(
            query=request.message,
            collection="regulatory_corpus",
            top_k=5,
        )

        # Build context from search results
        context = "\n\n".join(
            f"[Source: {r.get('source', 'N/A')}] {r.get('text', '')}" for r in results
        )

        # Generate response with LLM
        response = self.llm_factory.call(
            service_name="chat",
            messages=[{"role": "user", "content": request.message}],
            system_prompt=(
                "Answer based ONLY on the following regulatory context. "
                "Cite the specific article or source for every assertion.\n\n"
                f"Context:\n{context}"
            ),
        )

        yield {
            "type": "response",
            "content": response["content"],
            "sources": [{"source": r.get("source"), "score": r.get("score")} for r in results],
        }

    async def _execute_agent(self, request: CopilotRequest,
                             execution_id: str) -> AsyncGenerator[dict, None]:
        """AGENT_TOOLS: single specialized agent with database tools."""
        # Determine which agent to use based on module context
        agent_name = request.module_context or "privacy"
        yield {"type": "agent_started", "agent": agent_name, "action": f"Executing {agent_name} agent"}

        agent = self.agent_registry.get(agent_name)
        if not agent:
            yield {"type": "error", "message": f"Agent '{agent_name}' not found"}
            return

        result = agent.execute(task_id=execution_id, params={"message": request.message})
        yield {"type": "agent_completed", "result": result.get("output", {})}

    async def _execute_orchestration(self, request: CopilotRequest,
                                     execution_id: str) -> AsyncGenerator[dict, None]:
        """ORCHESTRATE: multi-agent coordination for complex tasks.

        Example DPIA workflow:
        1. PrivacyAgent: analyze treatment
        2. RiskAgent: assess risks to data subject rights
        3. ComplianceAgent: verify Art. 35 criteria
        4. ReportWriterAgent: generate formal DPIA document
        """
        steps = [
            {"agent": "privacy", "action": "analyze_treatment"},
            {"agent": "risk", "action": "assess_risks"},
            {"agent": "compliance", "action": "verify_compliance"},
            {"agent": "report_writer", "action": "generate_report"},
        ]

        state = {}
        for step_def in steps:
            agent_name = step_def["agent"]
            yield {
                "type": "step_transition",
                "agent": agent_name,
                "action": step_def["action"],
            }

            agent = self.agent_registry.get(agent_name)
            if agent:
                result = agent.execute(
                    task_id=f"{execution_id}_{agent_name}",
                    params={"message": request.message, "state": state},
                )
                state[agent_name] = result.get("output", {})
                yield {"type": "agent_completed", "agent": agent_name, "summary": str(result.get("output", {}))[:200]}

        yield {"type": "orchestration_complete", "agents_executed": len(steps)}

    async def _log_blocked_request(self, request, guard_result, execution_id):
        """Log blocked requests in audit_trail for security review."""
        # In production: persist to audit_trail table and forward to SIEM
        pass
