"""
Chapter 14: Copilot Orchestrator — 3 execution modes.

The Orchestrator classifies user intent and routes to the right mode:
  1. Chat+RAG:      informational queries answered with RAG context
  2. Agent+Tools:   action requests executed with tool invocations
  3. Orchestrate:   complex workflows with DAG-based team execution

Intent classification uses a 2-layer classifier (Chapter 13):
  Layer 1: pattern matching + keyword detection
  Layer 2: confidence scoring with threshold 0.75

The Orchestrator also coordinates:
  - Input guardrails (prompt injection, PII, off-topic)
  - Output guardrails (credential leak, system prompt exposure)
  - Streaming via SSE (Server-Sent Events)
"""

import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, Set, List, Optional, Any

from .base_agent import (
    AgentDefinition,
    AgentType,
    ExecutionMode,
    SecurityContext,
)


# =============================================================================
# Intent classification (Chapter 13 + Chapter 14)
# =============================================================================

@dataclass
class ClassifiedIntent:
    """Result of the 2-layer intent classifier."""
    mode: ExecutionMode
    confidence: float
    agent_slug: Optional[str] = None
    workflow_id: Optional[str] = None


INTENT_THRESHOLD = 0.75  # Empirically calibrated (Chapter 13)


def classify_intent(message: str, available_agents: list) -> ClassifiedIntent:
    """
    Two-layer intent classifier.

    Layer 1: Pattern matching + keyword detection (fast, no LLM call)
    Layer 2: Confidence scoring per intent category

    If confidence < 0.75, defaults conservatively to CHAT_RAG.
    """
    message_lower = message.lower()

    # Layer 1: Pattern matching for workflow triggers
    WORKFLOW_PATTERNS = {
        "genera una propuesta":   "full_bid_preparation",
        "prepara una oferta":     "full_bid_preparation",
        "analiza este documento":  "quick_analysis",
    }

    for pattern, workflow_id in WORKFLOW_PATTERNS.items():
        if pattern in message_lower:
            return ClassifiedIntent(
                mode=ExecutionMode.ORCHESTRATE,
                confidence=0.90,
                workflow_id=workflow_id,
            )

    # Layer 1: Action keywords -> Agent+Tools
    ACTION_KEYWORDS = [
        "busca", "encuentra", "actualiza", "crea", "genera",
        "modifica", "elimina", "exporta", "calcula",
    ]
    if any(kw in message_lower for kw in ACTION_KEYWORDS):
        return ClassifiedIntent(
            mode=ExecutionMode.AGENT_TOOLS,
            confidence=0.80,
        )

    # Default: Chat+RAG (conservative fallback)
    return ClassifiedIntent(
        mode=ExecutionMode.CHAT_RAG,
        confidence=0.85,
    )


# =============================================================================
# Team execution — DAG with parallel tasks (Chapter 14)
# =============================================================================

TEAM_TEMPLATES = {
    "full_bid_preparation": {
        "name": "Full Bid Preparation",
        "description": "Analyze requirements, search team, generate proposal, evaluate",
        "tasks": [
            {
                "task_id": "analyze_requirements",
                "title": "Requirements Analysis",
                "agent_slug": "analizar_requisitos",
                "depends_on": [],
            },
            {
                "task_id": "search_team",
                "title": "Team Search",
                "agent_slug": "perfiles_certificaciones",
                "depends_on": ["analyze_requirements"],
                "input_mappings": {
                    "query": "task.analyze_requirements.output.requirements_summary"
                },
            },
            {
                "task_id": "search_products",
                "title": "Product Catalog",
                "agent_slug": "experto_catalogo",
                "depends_on": ["analyze_requirements"],
                # search_team and search_products run IN PARALLEL
            },
            {
                "task_id": "search_references",
                "title": "Similar Projects",
                "agent_slug": "buscador_referencias",
                "depends_on": ["analyze_requirements"],
                # Also parallel with search_team and search_products
            },
            {
                "task_id": "generate_offer",
                "title": "Technical Proposal Generation",
                "agent_slug": "generador_propuestas",
                "depends_on": [
                    "analyze_requirements",
                    "search_team",
                    "search_products",
                    "search_references",
                ],
                # Waits for ALL searches to complete
            },
            {
                "task_id": "evaluate_offer",
                "title": "Proposal Evaluation",
                "agent_slug": "evaluador_propuestas",
                "depends_on": ["generate_offer"],
            },
        ],
    },
    "quick_analysis": {
        "name": "Quick Analysis",
        "tasks": [
            {"task_id": "analyze", "agent_slug": "analizar_requisitos", "depends_on": []},
            {"task_id": "team", "agent_slug": "perfiles_certificaciones", "depends_on": ["analyze"]},
            {"task_id": "products", "agent_slug": "experto_catalogo", "depends_on": ["analyze"]},
        ],
    },
}


@dataclass
class TaskState:
    """Runtime state of a task within a team execution."""
    task_id: str
    status: str = "pending"     # pending, running, completed, failed
    output: Optional[dict] = None
    error: Optional[str] = None


class TeamExecutor:
    """
    Execute a DAG of tasks with parallelism on independent tasks.

    Chapter 14: A 6-task flow that takes 8 minutes sequentially
    completes in 3.5 minutes because the three searches run simultaneously.
    """

    async def execute_team(
        self, template_id: str, initial_input: dict
    ) -> AsyncGenerator[str, None]:
        """
        Execute a team template as a DAG.

        Yields SSE events: task_start, task_complete, task_failed, team_progress.
        """
        template = TEAM_TEMPLATES.get(template_id)
        if not template:
            yield f"event: error\ndata: Unknown template: {template_id}\n\n"
            return

        tasks = template["tasks"]
        states: Dict[str, TaskState] = {
            t["task_id"]: TaskState(task_id=t["task_id"]) for t in tasks
        }
        completed: Set[str] = set()
        failed: Set[str] = set()

        while len(completed) + len(failed) < len(tasks):
            # Find tasks whose dependencies are all completed
            ready = [
                t for t in tasks
                if t["task_id"] not in completed
                and t["task_id"] not in failed
                and all(d in completed for d in t.get("depends_on", []))
            ]

            if not ready:
                break  # Deadlock: failed dependencies or circular

            # Execute ready tasks in parallel
            for t in ready:
                yield f"event: task_start\ndata: {t['task_id']}\n\n"

            results = await asyncio.gather(
                *[self._execute_task(t, states) for t in ready],
                return_exceptions=True,
            )

            for task_cfg, result in zip(ready, results):
                tid = task_cfg["task_id"]
                if isinstance(result, Exception):
                    states[tid].status = "failed"
                    states[tid].error = str(result)
                    failed.add(tid)
                    yield f"event: task_failed\ndata: {tid}\n\n"
                else:
                    states[tid].status = "completed"
                    states[tid].output = result
                    completed.add(tid)
                    yield f"event: task_complete\ndata: {tid}\n\n"

            progress = len(completed) / len(tasks) * 100
            yield f"event: team_progress\ndata: {progress:.0f}\n\n"

    async def _execute_task(
        self, task_config: dict, states: Dict[str, TaskState]
    ) -> dict:
        """
        Execute a single task by delegating to the assigned agent.

        Input mappings resolve data from previous task outputs:
          "query": "task.analyze_requirements.output.requirements_summary"
        """
        # Resolve input mappings from completed task outputs
        resolved_input = {}
        for key, mapping in task_config.get("input_mappings", {}).items():
            if mapping.startswith("task."):
                parts = mapping.split(".")
                source_task = parts[1]
                output_key = parts[3] if len(parts) > 3 else "result"
                source_output = states.get(source_task, TaskState(task_id="")).output
                if source_output:
                    resolved_input[key] = source_output.get(output_key, "")

        # In production: load agent via AgentLoader and execute
        # agent = agent_loader.load_agent(task_config["agent_slug"])
        # result = await agent.execute(resolved_input)
        return {"result": f"Completed: {task_config['task_id']}"}
