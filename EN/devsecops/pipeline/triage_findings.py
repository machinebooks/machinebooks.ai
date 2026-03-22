# Source: The DevSecOps and the Machine -- Chapter 1
# Pattern: SARIF-based SAST triage with Claude

# scripts/triage_findings.py
"""
Intelligent triage of SAST findings using Claude.
First prototype — the complete agent is developed in Chapter 9.
"""
import json
import sys
from pathlib import Path
import anthropic

def load_sarif(path: str) -> list[dict]:
    """Load SARIF findings and extract relevant fields."""
    with open(path) as f:
        sarif = json.load(f)

    findings = []
    for run in sarif.get("runs", []):
        tool_name = run["tool"]["driver"]["name"]
        for result in run.get("results", []):
            location = result["locations"][0]["physicalLocation"]
            file_path = location["artifactLocation"]["uri"]
            region = location.get("region", {})
            findings.append({
                "rule_id": result["ruleId"],
                "message": result["message"]["text"],
                "severity": result.get("level", "warning"),
                "file": file_path,
                "line": region.get("startLine", 0),
                "tool": tool_name,
            })
    return findings


def triage_finding(client: anthropic.Anthropic, finding: dict,
                   code_context: str) -> dict:
    """Send a finding to Claude for triage with code context."""
    prompt = f"""You are an expert security analyst. Analyze this SAST
finding and determine whether it is a true positive or a false positive.

## Finding
- Rule: {finding['rule_id']}
- Message: {finding['message']}
- Reported severity: {finding['severity']}
- File: {finding['file']}
- Line: {finding['line']}

## Source code (context)