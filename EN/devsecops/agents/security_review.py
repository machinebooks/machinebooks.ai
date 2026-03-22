# Source: The DevSecOps and the Machine -- Chapter 10
# Pattern: AI security code review for pull requests

# .github/scripts/security_review.py
import json
import os
from pathlib import Path

import anthropic
from github import Github

# Configuration from environment variables
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
REPO_NAME = os.environ["REPO_NAME"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)


def get_pr_context() -> dict:
    """Gets diff and content of modified files."""
    diff_text = Path("pr_diff.txt").read_text(encoding="utf-8")

    # Retrieve complete content of modified files
    # so the agent has context beyond the diff
    modified_files = {}
    for f in pr.get_files():
        if f.status != "removed" and f.filename.endswith(
            (".py", ".ts", ".tsx", ".js", ".jsx", ".yaml", ".yml")
        ):
            try:
                content = repo.get_contents(
                    f.filename, ref=pr.head.sha
                )
                modified_files[f.filename] = content.decoded_content.decode()
            except Exception:
                pass  # Binary or inaccessible file

    return {"diff": diff_text, "files": modified_files}

REVIEW_SYSTEM_PROMPT = """You are a senior application security reviewer.
Your job is to analyze a pull request diff and detect insecure patterns
that conventional SAST tools do not cover.

## Project technology stack
- Backend: FastAPI + SQLAlchemy 2.0 + Alembic
- Frontend: React 18 + TypeScript
- Auth: @require_auth and @require_role(role) decorators
- ORM: SQLAlchemy with declarative models
- DB: PostgreSQL with prepared statements via SQLAlchemy

## Security patterns to look for

1. AUTH: Endpoints without @require_auth or equivalent.
   Endpoints accessing resources by ID without verifying
   current_user.id == resource.owner_id.

2. INPUT: HTTP parameters used without type or range validation.
   Uploaded files without real MIME type verification.

3. SQLI: Queries with f-strings or concatenation instead of
   SQLAlchemy prepared parameters.

4. XSS: User values rendered without escaping.
   dangerouslySetInnerHTML with unsanitized data.

5. IDOR: Resources accessible by ID without ownership verification.
   Admin endpoints without role verification.

6. RACE: Read-modify-write operations without atomic transaction
   or locking. Quota checks separated from the operation
   that consumes the quota.

7. CRYPTO: MD5/SHA1 for passwords. random instead of secrets.
   Hardcoded keys. Hash comparisons without constant time.

8. INFO: Stack traces in production responses. Sensitive data
   in logs. User enumeration through different error messages.

## Output rules

- Only report findings with HIGH or MEDIUM confidence.
- Do NOT report style, performance, or readability improvements.
- Each finding MUST include: file, approximate line, category
  (AUTH/INPUT/SQLI/XSS/IDOR/RACE/CRYPTO/INFO), severity
  (critical/high/medium), 2-3 sentence explanation, suggested fix
  as code, and confidence level (high/medium).
- If you find no security findings, respond with an empty JSON.
- Respond EXCLUSIVELY with valid JSON, no additional text."""


def build_review_prompt(context: dict) -> str:
    """Builds the user prompt with diff and context."""
    files_context = ""
    for filename, content in context["files"].items():
        # Limit context per file to avoid exceeding tokens
        truncated = content[:3000] if len(content) > 3000 else content
        files_context += f"\n--- {filename} (complete) ---\n{truncated}\n"

    return f"""Analyze this pull request for security vulnerabilities.

## PR Diff

def analyze_pr(context: dict) -> list[dict]:
    """Sends the diff to Claude and obtains security findings."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=REVIEW_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_review_prompt(context),
            }
        ],
    )

    response_text = message.content[0].text

    try:
        result = json.loads(response_text)
        return result.get("findings", [])
    except json.JSONDecodeError:
        # If Claude does not return valid JSON, try extracting it
        # by finding the first { and the last }
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(response_text[start:end])
            return result.get("findings", [])
        return []

def publish_findings(findings: list[dict]) -> None:
    """Publishes findings as review comments on the PR."""
    if not findings:
        # No findings: leave a positive general comment
        pr.create_issue_comment(
            "🔒 **Security Review (AI)**: No insecure patterns "
            "detected in this PR.\n\n"
            "_Automated review with Claude claude-sonnet-4-6. "
            "Does not replace human security review._"
        )
        return

    # Get the latest commit from the PR to position comments
    commit = repo.get_commit(pr.head.sha)

    comments_body = []
    for finding in findings:
        severity_icon = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
        }.get(finding["severity"], "⚪")

        body = (
            f"{severity_icon} **[{finding['category']}]** "
            f"Severity: {finding['severity']} | "
            f"Confidence: {finding['confidence']}\n\n"
            f"{finding['explanation']}\n\n"
        )

        if finding.get("suggested_fix"):
            body += (
                f"**Suggested fix:**\n"
                f"```python\n{finding['suggested_fix']}\n```\n\n"
            )

        body += (
            "_Automated review. Mark with 👎 if false "
            "positive to improve future reviews._"
        )

        try:
            pr.create_review_comment(
                body=body,
                commit=commit,
                path=finding["file"],
                line=finding["line"],
            )
        except Exception:
            # If the comment cannot be positioned (line not in the diff),
            # publish as a general comment
            comments_body.append(
                f"**{finding['file']}:{finding['line']}**\n\n{body}"
            )

    if comments_body:
        pr.create_issue_comment(
            "🔒 **Security Review (AI)** — Findings not "
            "positionable in the diff:\n\n"
            + "\n---\n".join(comments_body)
        )

def main():
    """Entry point: context -> analysis -> publication."""
    print(f"Analyzing PR #{PR_NUMBER} in {REPO_NAME}...")

    # 1. Get PR context
    context = get_pr_context()

    diff_size = len(context["diff"])
    file_count = len(context["files"])
    print(f"Diff: {diff_size} characters, {file_count} files")

    # 2. Limit analysis to PRs with relevant code
    if diff_size < 10:
        print("Empty or minimal diff, skipping review.")
        return

    # 3. Analyze with Claude
    findings = analyze_pr(context)
    print(f"Findings detected: {len(findings)}")

    # 4. Filter by confidence (double check)
    filtered = [
        f for f in findings
        if f.get("confidence") in ("high", "medium")
    ]
    print(f"Findings after confidence filter: {len(filtered)}")

    # 5. Publish on the PR
    publish_findings(filtered)
    print("Security review published.")


if __name__ == "__main__":
    main()