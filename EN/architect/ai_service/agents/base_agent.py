"""
Chapter 14: BaseAgent with tools and AgentDefinition from database.

The Platform stores agent definitions in DB (AgentDefinition model)
so agents can be configured from the Admin UI without redeploy:
  - 4 types: assistant, autonomous, workflow, specialized
  - 3 execution modes: chat_rag, agent_tools, orchestrate
  - Tool assignments via M2M table with order and per-agent config
  - 60-second Redis cache via AgentLoader

Key patterns:
  - SecurityContext propagated to every tool invocation
  - Guardrails applied before and after Claude processes the message
  - 8 guardrail types with graduated actions: ALLOW -> SANITIZE -> BLOCK
"""

import enum
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


# =============================================================================
# Agent types and execution modes (Chapter 14)
# =============================================================================

class AgentType(enum.Enum):
    ASSISTANT = "assistant"       # Chat+RAG, simple tool use
    AUTONOMOUS = "autonomous"     # Full ReAct loop, multi-step
    WORKFLOW = "workflow"          # Activates Workflow Engine
    SPECIALIZED = "specialized"   # Domain-specific (CV, proposal, docs)


class ExecutionMode(enum.Enum):
    CHAT_RAG = "chat_rag"             # Informational queries with RAG
    AGENT_TOOLS = "agent_tools"       # Execution with tools
    ORCHESTRATE = "orchestrate"       # Predefined workflow activation


# =============================================================================
# SecurityContext (Chapter 14 + Chapter 6)
# =============================================================================

@dataclass
class SecurityContext:
    """
    Security context propagated to every tool invocation.

    Every tool — whether specific or universal — receives this context
    from the HTTP request headers, through the Copilot Orchestrator,
    to the tool execution. No tool runs without knowing who invoked it.
    """
    user_id: int = 0
    app_code: str = "operations"
    allowed_collections: List[str] = field(default_factory=list)
    is_internal: bool = False       # True for backend inter-service calls
    is_admin: bool = False
    project_id: Optional[int] = None
    client_id: Optional[int] = None

    def can_access_collection(self, collection: str) -> bool:
        """Check permissions on RAG collections (Chapter 6)."""
        SYSTEM_ONLY = {"opportunities_raw"}
        RESTRICTED = {"commercial_catalog", "project_history"}

        if collection in SYSTEM_ONLY:
            return self.is_internal
        if collection in RESTRICTED:
            return self.is_internal or self.is_admin
        if self.allowed_collections:
            return collection in self.allowed_collections
        return True  # Public collections


# =============================================================================
# AgentDefinition (Chapter 14 — from database)
# =============================================================================

@dataclass
class AgentDefinition:
    """
    Agent configuration loaded from database.

    In production this is a SQLAlchemy model in platform_core.
    The AgentLoader caches definitions in Redis (60s TTL).
    """
    slug: str
    name: str
    agent_type: AgentType
    execution_mode: ExecutionMode
    model_id: str = "claude-sonnet-4-6"
    temperature: float = 0.3
    max_tokens: int = 4096
    system_prompt: str = ""
    max_iterations: int = 10
    tools: List[str] = field(default_factory=list)
    intent_keywords: List[str] = field(default_factory=list)
    status: str = "active"

    @classmethod
    def from_dict(cls, data: dict) -> "AgentDefinition":
        return cls(
            slug=data["slug"],
            name=data["name"],
            agent_type=AgentType(data["agent_type"]),
            execution_mode=ExecutionMode(data["execution_mode"]),
            model_id=data.get("model_id", "claude-sonnet-4-6"),
            temperature=data.get("temperature", 0.3),
            max_tokens=data.get("max_tokens", 4096),
            system_prompt=data.get("system_prompt", ""),
            max_iterations=data.get("max_iterations", 10),
            tools=data.get("tools", []),
            intent_keywords=data.get("intent_keywords", []),
        )


# =============================================================================
# AgentLoader with Redis cache (Chapter 14)
# =============================================================================

class AgentLoader:
    """Load and cache agent definitions from database."""

    CACHE_TTL = 60  # seconds

    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client

    def load_agent(self, slug: str) -> Optional[AgentDefinition]:
        """
        Load agent by slug with 60-second Redis cache.

        Cache hit: ~1ms (Redis). Cache miss: ~5ms (DB query).
        Changes in the Agent Studio UI are reflected within 60 seconds
        without restarting the AI service.
        """
        cache_key = f"agent_def:{slug}"
        cached = self.redis.get(cache_key)
        if cached:
            return AgentDefinition.from_dict(json.loads(cached))

        # Fallback to database
        # agent = self.db.query(AgentDefinitionModel).filter_by(
        #     slug=slug, status="active"
        # ).first()
        # if agent:
        #     self.redis.setex(cache_key, self.CACHE_TTL, json.dumps(agent.to_dict()))
        # return agent

        return None


# =============================================================================
# Universal Agent Tools (Chapter 14)
# =============================================================================

UNIVERSAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read file contents. Supports .docx (text by sections with headings), "
                ".xlsx/.xlsm (sheet structure and cells), .pdf (extracted text), "
                ".txt/.json/.csv (raw content). For .docx also returns table index."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "section": {
                        "type": "string",
                        "description": "Optional: specific heading section (.docx)",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": (
                "Search the Platform's knowledge bases. Scopes: 'rag' (document vectors), "
                "'opportunities' (Meilisearch index), 'profiles' (CV database), "
                "'products' (service catalog)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language query"},
                    "scope": {
                        "type": "string",
                        "enum": ["rag", "opportunities", "profiles", "products"],
                        "description": "Which knowledge base to search",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results (1-10)",
                        "default": 5,
                    },
                },
                "required": ["query", "scope"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "done",
            "description": "Signal that the task is complete with a summary of results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Task completion summary"},
                },
                "required": ["summary"],
            },
        },
    },
    # edit_file, write_file, run_command omitted for brevity
    # See Chapter 14 for the full 6-tool universal set
]
