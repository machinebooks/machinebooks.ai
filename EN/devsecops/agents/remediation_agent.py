# Source: The DevSecOps and the Machine -- Chapter 11
# Pattern: Automated remediation agent with PR generation

"""remediation_agent.py — Remediation agent with Claude Agent SDK."""
import anthropic
import json
from pathlib import Path

client = anthropic.Anthropic()

# Remediation agent tool definitions
tools = [
    {
        "name": "read_file",
        "description": (
            "Reads the contents of a repository file. "
            "Use this tool to understand the code affected "
            "by the vulnerability before generating a fix."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Relative path to the file"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Start line (optional)"
                },
                "end_line": {
                    "type": "integer",
                    "description": "End line (optional)"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "read_changelog",
        "description": (
            "Queries a dependency's changelog to "
            "identify breaking changes between two versions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string"},
                "current_version": {"type": "string"},
                "target_version": {"type": "string"}
            },
            "required": [
                "package_name",
                "current_version",
                "target_version"
            ]
        }
    },
    {
        "name": "create_branch",
        "description": (
            "Creates a new branch in the repository to "
            "apply the fix. Never modifies main directly."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "branch_name": {"type": "string"},
                "base_branch": {
                    "type": "string",
                    "default": "main"
                }
            },
            "required": ["branch_name"]
        }
    },
    {
        "name": "apply_fix",
        "description": (
            "Applies changes to a file on the fix branch. "
            "Receives the complete new file content."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "new_content": {"type": "string"},
                "commit_message": {"type": "string"}
            },
            "required": [
                "file_path", "new_content", "commit_message"
            ]
        }
    },
    {
        "name": "create_pull_request",
        "description": (
            "Creates a GitHub pull request with the "
            "applied fix, explanation, and labels."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string"},
                "branch": {"type": "string"},
                "labels": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "reviewers": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["title", "body", "branch"]
        }
    },
    {
        "name": "check_exclusion_policy",
        "description": (
            "Checks whether the finding is excluded from "
            "automatic remediation by OPA policies."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "finding_id": {"type": "string"},
                "file_path": {"type": "string"},
                "fix_category": {"type": "string"}
            },
            "required": [
                "finding_id", "file_path", "fix_category"
            ]
        }
    }
]

"""tools_impl.py — Tool implementation with GitHub API."""
from github import Github, GithubException
from functools import lru_cache
import subprocess
import json

# Token with permissions: contents (write), pull_requests (write)
gh = Github("<YOUR_GITHUB_TOKEN>")
repo = gh.get_repo("<YOUR_ORG>/<YOUR_REPO>")

def read_file(file_path: str,
              start_line: int = None,
              end_line: int = None) -> dict:
    """Reads a repository file's content."""
    try:
        content = repo.get_contents(file_path, ref="main")
        decoded = content.decoded_content.decode("utf-8")
        lines = decoded.split("\n")

        if start_line and end_line:
            lines = lines[start_line - 1:end_line]

        return {
            "content": "\n".join(lines),
            "total_lines": len(decoded.split("\n")),
            "sha": content.sha
        }
    except GithubException as e:
        return {"error": f"Could not read {file_path}: {e}"}

def create_branch(branch_name: str,
                  base_branch: str = "main") -> dict:
    """Creates a new branch from base_branch."""
    try:
        base = repo.get_branch(base_branch)
        ref = repo.create_git_ref(
            f"refs/heads/{branch_name}",
            base.commit.sha
        )
        return {
            "branch": branch_name,
            "sha": ref.object.sha,
            "status": "created"
        }
    except GithubException as e:
        return {"error": f"Could not create branch: {e}"}

def apply_fix(file_path: str,
              new_content: str,
              commit_message: str,
              branch: str) -> dict:
    """Applies a change to a file on the fix branch."""
    try:
        # Get current file SHA
        current = repo.get_contents(file_path, ref=branch)
        result = repo.update_file(
            path=file_path,
            message=commit_message,
            content=new_content,
            sha=current.sha,
            branch=branch
        )
        return {
            "commit_sha": result["commit"].sha,
            "status": "applied"
        }
    except GithubException as e:
        return {"error": f"Could not apply fix: {e}"}

def create_pull_request(title: str,
                        body: str,
                        branch: str,
                        labels: list = None,
                        reviewers: list = None) -> dict:
    """Creates a PR with the fix and assigns reviewers."""
    try:
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch,
            base="main"
        )
        if labels:
            pr.set_labels(*labels)
        if reviewers:
            pr.create_review_request(reviewers=reviewers)

        return {
            "pr_number": pr.number,
            "pr_url": pr.html_url,
            "status": "created"
        }
    except GithubException as e:
        return {"error": f"Could not create PR: {e}"}

REMEDIATION_SYSTEM_PROMPT = """You are a security remediation agent.
Your function is to generate fixes for security findings and create
pull requests on GitHub.

## Operating rules

1. NEVER modify code on the main branch. Always create a new branch
   with the prefix `security-fix/`.

2. BEFORE generating a fix, verify with check_exclusion_policy that
   the finding is not excluded from automatic remediation.

3. ALWAYS read the affected file completely before proposing changes.
   Do not generate fixes based solely on the finding description.

4. For dependency updates, ALWAYS consult the changelog
   to identify breaking changes.

5. The PR must include:
   - Title: "fix(security): [CVE-ID or CWE-ID] brief description"
   - Body: vulnerability explanation, what the fix changes,
     residual risk, reference to the triage finding
   - Labels: security-fix, auto-remediation, severity
   - Reviewers: the owner team of the affected service

6. If your confidence in the fix is below 80%, generate an advisory PR
   without code changes. Use the needs-human-review label.

7. Do not modify more than 50 lines in a single fix. If the change
   requires more, generate an advisory PR.

8. Each fix must be atomic: one finding, one PR, one coherent
   change. Do not group multiple fixes in a PR.

## Response format

For each finding, respond with:
- decision: "auto_fix" | "advisory_only" | "excluded"
- confidence: 0-100
- reasoning: why you chose this action
- If auto_fix: generate the fix using the tools
- If advisory_only: generate the description and suggestion
"""

"""remediation_orchestrator.py — Remediation orchestrator."""
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

def remediate_finding(finding: dict) -> dict:
    """Processes a finding and generates a remediation PR."""
    # Build finding context for the agent
    context = build_finding_context(finding)

    messages = [
        {
            "role": "user",
            "content": (
                f"Remediate the following security finding:\n\n"
                f"{json.dumps(context, indent=2, ensure_ascii=False)}\n\n"
                f"Follow the operating rules. Start by verifying "
                f"the exclusion policy, then read the affected "
                f"code, and decide whether to generate auto_fix or advisory."
            )
        }
    ]

    # Agentic loop: the agent calls tools until completion
    max_iterations = 15
    for _ in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=REMEDIATION_SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        # Process model response
        if response.stop_reason == "end_turn":
            # The agent finished — extract result
            return extract_result(response, finding)

        if response.stop_reason == "tool_use":
            # The agent wants to use a tool
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(
                        block.name, block.input
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            # Add model response and results
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })

    return {
        "status": "max_iterations_reached",
        "finding_id": finding["id"]
    }


def execute_tool(name: str, params: dict) -> dict:
    """Executes a tool and returns the result."""
    tool_map = {
        "read_file": read_file,
        "read_changelog": read_changelog,
        "create_branch": create_branch,
        "apply_fix": apply_fix,
        "create_pull_request": create_pull_request,
        "check_exclusion_policy": check_exclusion_policy,
    }
    fn = tool_map.get(name)
    if not fn:
        return {"error": f"Unknown tool: {name}"}
    return fn(**params)