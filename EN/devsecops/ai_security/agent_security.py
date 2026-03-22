# Source: The DevSecOps and the Machine -- Chapter 15
# Pattern: Agent permission system, rate limiting, audit trail

from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Any

class RiskLevel(Enum):
    """Risk classification for agent tools."""
    READ = "read"           # Data reading, no side effect
    ANALYZE = "analyze"     # Running scans, querying APIs
    MODIFY = "modify"       # Creating branches, PRs, files
    DESTRUCTIVE = "destruct"  # Merge, deploy, revocation, deletion

@dataclass
class SecureTool:
    """Tool wrapper with security metadata."""
    name: str
    func: Callable
    risk_level: RiskLevel
    description: str
    max_calls_per_run: int = 50    # Invocation limit per execution
    requires_approval: bool = False # Mandatory human gate
    allowed_args: dict = field(default_factory=dict)  # Argument restriction

@dataclass
class AgentPermissions:
    """Permission profile for a pipeline agent."""
    agent_name: str
    allowed_risk_levels: list[RiskLevel]
    max_total_tool_calls: int = 100
    max_tokens_budget: int = 50_000
    max_execution_seconds: int = 300
    human_approval_channel: str = "slack://security-approvals"

# Predefined profiles for pipeline agents
TRIAGE_AGENT_PERMS = AgentPermissions(
    agent_name="triage-agent",
    allowed_risk_levels=[RiskLevel.READ, RiskLevel.ANALYZE],
    max_total_tool_calls=200,
    max_tokens_budget=100_000,
    max_execution_seconds=600,
)

REMEDIATION_AGENT_PERMS = AgentPermissions(
    agent_name="remediation-agent",
    allowed_risk_levels=[RiskLevel.READ, RiskLevel.ANALYZE, RiskLevel.MODIFY],
    max_total_tool_calls=50,
    max_tokens_budget=80_000,
    max_execution_seconds=300,
)

import time
from dataclasses import dataclass, field

@dataclass
class BudgetState:
    """Accumulated consumption state of the agent."""
    tool_calls: int = 0
    tokens_used: int = 0
    start_time: float = field(default_factory=time.time)
    actions_log: list = field(default_factory=list)

class BudgetExceeded(Exception):
    """The agent has exceeded its assigned budget."""
    def __init__(self, dimension: str, limit: int, actual: int):
        self.dimension = dimension
        self.limit = limit
        self.actual = actual
        super().__init__(
            f"Budget exceeded: {dimension} "
            f"(limit={limit}, actual={actual})"
        )

class AgentBudgetGuard:
    """Circuit breaker that stops the agent when limits are exceeded."""

    def __init__(self, permissions: AgentPermissions):
        self.permissions = permissions
        self.state = BudgetState()

    def check_budget(self) -> None:
        """Verifies budget before each invocation."""
        elapsed = time.time() - self.state.start_time

        if self.state.tool_calls >= self.permissions.max_total_tool_calls:
            raise BudgetExceeded(
                "tool_calls",
                self.permissions.max_total_tool_calls,
                self.state.tool_calls,
            )
        if self.state.tokens_used >= self.permissions.max_tokens_budget:
            raise BudgetExceeded(
                "tokens",
                self.permissions.max_tokens_budget,
                self.state.tokens_used,
            )
        if elapsed >= self.permissions.max_execution_seconds:
            raise BudgetExceeded(
                "execution_seconds",
                self.permissions.max_execution_seconds,
                int(elapsed),
            )

    def record_call(self, tool_name: str, tokens: int, args: dict):
        """Records each invocation for auditing and control."""
        self.state.tool_calls += 1
        self.state.tokens_used += tokens
        self.state.actions_log.append({
            "tool": tool_name,
            "tokens": tokens,
            "args_summary": _sanitize_args(args),
            "timestamp": time.time(),
            "cumulative_calls": self.state.tool_calls,
        })

def _sanitize_args(args: dict) -> dict:
    """Removes sensitive values before logging."""
    sensitive_keys = {"api_key", "token", "password", "secret"}
    return {
        k: "***REDACTED***" if k in sensitive_keys else v
        for k, v in args.items()
    }

import anthropic
from typing import Any

class SecureAgentRunner:
    """Agent executor with integrated security controls."""

    def __init__(
        self,
        permissions: AgentPermissions,
        tools: list[SecureTool],
        system_prompt: str,
    ):
        self.permissions = permissions
        self.budget = AgentBudgetGuard(permissions)
        self.tools = self._filter_tools(tools)
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic()
        self.audit_log: list[dict] = []

    def _filter_tools(self, tools: list[SecureTool]) -> list[SecureTool]:
        """Only admits tools at the permitted risk level."""
        allowed = []
        for tool in tools:
            if tool.risk_level in self.permissions.allowed_risk_levels:
                allowed.append(tool)
            else:
                self.audit_log.append({
                    "event": "tool_rejected",
                    "tool": tool.name,
                    "risk_level": tool.risk_level.value,
                    "reason": "Risk level not permitted",
                })
        return allowed

    def _execute_tool(self, tool: SecureTool, args: dict) -> Any:
        """Executes a tool with budget verification."""
        # 1. Verify budget before executing
        self.budget.check_budget()

        # 2. Check if human approval is required
        if tool.requires_approval:
            approval = self._request_human_approval(tool, args)
            if not approval.approved:
                return {"status": "rejected", "reason": approval.reason}

        # 3. Verify the tool's individual limit
        tool_calls = sum(
            1 for a in self.budget.state.actions_log
            if a["tool"] == tool.name
        )
        if tool_calls >= tool.max_calls_per_run:
            return {
                "status": "limit_reached",
                "message": f"{tool.name}: maximum {tool.max_calls_per_run} "
                           f"invocations per execution",
            }

        # 4. Execute the tool
        result = tool.func(**args)

        # 5. Record the invocation
        self.budget.record_call(tool.name, tokens=0, args=args)

        return result

    def _request_human_approval(
        self, tool: SecureTool, args: dict,
    ) -> "ApprovalResponse":
        """Sends an approval request and waits for a response."""
        # Implementation connects with Slack/webhook/email
        # based on self.permissions.human_approval_channel
        ...

    def run(self, task: str) -> dict:
        """Executes the agent with all security layers."""
        try:
            # Build the tool list for Claude
            tool_definitions = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": _get_schema(t.func),
                }
                for t in self.tools
            ]

            # Invoke Claude with the filtered tools
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=self.system_prompt,
                tools=tool_definitions,
                messages=[{"role": "user", "content": task}],
            )

            # Process tool_use in the response (agent loop)
            return self._agent_loop(response)

        except BudgetExceeded as e:
            self.audit_log.append({
                "event": "budget_exceeded",
                "dimension": e.dimension,
                "limit": e.limit,
                "actual": e.actual,
            })
            return {
                "status": "budget_exceeded",
                "partial_results": self.budget.state.actions_log,
                "error": str(e),
            }

import uuid
import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("agent.audit")

@dataclass
class SecurityContext:
    """Security context for each agent action."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    agent_run_id: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    action: str = ""              # Name of the invoked tool
    risk_level: str = ""          # read / analyze / modify / destruct
    args_sanitized: dict = field(default_factory=dict)
    result_summary: str = ""      # Result summary (not the full result)
    outcome: str = ""             # success / failure / rejected / budget_exceeded
    approved_by: str | None = None  # ID of the human who approved, if applicable
    tokens_consumed: int = 0
    execution_ms: int = 0

class AgentAuditMiddleware:
    """Middleware that logs each action with SecurityContext."""

    def __init__(self, agent_name: str, run_id: str):
        self.agent_name = agent_name
        self.run_id = run_id
        self.contexts: list[SecurityContext] = []

    def log_action(
        self,
        tool: SecureTool,
        args: dict,
        result: Any,
        outcome: str,
        approved_by: str | None = None,
        tokens: int = 0,
        duration_ms: int = 0,
    ) -> SecurityContext:
        """Creates and persists a SecurityContext for the action."""
        ctx = SecurityContext(
            agent_name=self.agent_name,
            agent_run_id=self.run_id,
            action=tool.name,
            risk_level=tool.risk_level.value,
            args_sanitized=_sanitize_args(args),
            result_summary=_summarize_result(result),
            outcome=outcome,
            approved_by=approved_by,
            tokens_consumed=tokens,
            execution_ms=duration_ms,
        )
        self.contexts.append(ctx)

        # Structured logging for SIEM / Elasticsearch / Loki
        logger.info(
            json.dumps(asdict(ctx), ensure_ascii=False)
        )
        return ctx

    def get_run_summary(self) -> dict:
        """Generates a summary of the agent's complete execution."""
        return {
            "agent": self.agent_name,
            "run_id": self.run_id,
            "total_actions": len(self.contexts),
            "outcomes": _count_outcomes(self.contexts),
            "risk_distribution": _count_risk_levels(self.contexts),
            "total_tokens": sum(c.tokens_consumed for c in self.contexts),
            "approvals_required": sum(
                1 for c in self.contexts if c.approved_by
            ),
        }

def _summarize_result(result: Any) -> str:
    """Safe summary of the result, without sensitive data."""
    if isinstance(result, dict):
        return json.dumps(
            {k: type(v).__name__ for k, v in result.items()}
        )
    return str(result)[:200]

def _count_outcomes(contexts: list[SecurityContext]) -> dict:
    counts: dict[str, int] = {}
    for ctx in contexts:
        counts[ctx.outcome] = counts.get(ctx.outcome, 0) + 1
    return counts

def _count_risk_levels(contexts: list[SecurityContext]) -> dict:
    counts: dict[str, int] = {}
    for ctx in contexts:
        counts[ctx.risk_level] = counts.get(ctx.risk_level, 0) + 1
    return counts