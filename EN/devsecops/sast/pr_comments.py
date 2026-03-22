# Source: The DevSecOps and the Machine -- Chapter 4
# Pattern: Publish triage results as inline PR comments

import requests

def publish_pr_comment(
    repo: str, pr_number: int, finding: dict, token: str
):
    """Publish an inline comment on the PR with the triaged finding."""
    triage = finding["triage_sonnet"]
    body = f"""### {triage['adjusted_severity'].upper()}: {finding['check_id']}

**Classification:** {triage['classification']}

**Justification:** {triage['justification']}

**Attack vector:** {triage['attack_vector']}

**Suggested remediation:** {triage['remediation']}

---
_Finding detected by Semgrep, triaged by Claude (claude-sonnet-4-6)_"""

    requests.post(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        json={
            "body": body,
            "commit_id": finding.get("commit_id", "HEAD"),
            "path": finding["path"],
            "line": finding["start"]["line"],
            "side": "RIGHT",
        },
    )

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Semgrep JSON file")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="PR number")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    findings = data.get("results", [])
    print(f"Semgrep reported {len(findings)} findings")

    # Tiered triage: Haiku filters, Sonnet analyzes
    triaged = tiered_triage(findings)
    print(f"After triage: {len(triaged)} relevant findings")

    # Publish comments on the PR
    critical_count = 0
    for h in triaged:
        publish_pr_comment(args.repo, args.pr, h, os.environ["GITHUB_TOKEN"])
        if h["triage_sonnet"]["adjusted_severity"] in ("critical", "high"):
            critical_count += 1

    # Gate: fail pipeline if there are critical findings
    if critical_count > 0:
        print(f"BLOCKED: {critical_count} high/critical severity findings")
        sys.exit(1)

    print("SAST pipeline passed: no confirmed critical findings")