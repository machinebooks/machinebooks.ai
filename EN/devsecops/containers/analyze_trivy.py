# Source: The DevSecOps and the Machine -- Chapter 7
# Pattern: Contextual Trivy result analysis with Claude

import anthropic
import json
from pathlib import Path

def load_trivy_results(path: str) -> dict:
    """Load Trivy results from JSON file."""
    return json.loads(Path(path).read_text())

def build_analysis_prompt(results: dict, context: dict) -> str:
    """Build prompt with results and service context."""
    vulns = []
    for result in results.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            vulns.append({
                "id": vuln["VulnerabilityID"],
                "severity": vuln["Severity"],
                "pkg": vuln["PkgName"],
                "installed": vuln["InstalledVersion"],
                "fixed": vuln.get("FixedVersion", "no fix available"),
                "title": vuln.get("Title", ""),
            })

    return f"""Analyze these Trivy findings for the
{context['service_name']} service image.

Service context:
- Internet-facing: {context['internet_facing']}
- Sensitive data: {context['handles_sensitive_data']}
- Current base image: {context['base_image']}

Findings ({len(vulns)} vulnerabilities):
{json.dumps(vulns, indent=2)}

Generate a report with:
1. Findings requiring immediate action (with justification)
2. For each critical finding: concrete remediation steps
3. Findings that can be temporarily accepted (with justification)
4. If applicable: base image change recommendation
5. Specific Dockerfile changes to reduce surface"""

def analyze_trivy_results():
    """Execute Trivy results analysis with Claude."""
    client = anthropic.Anthropic()

    image_results = load_trivy_results("trivy-image.json")
    config_results = load_trivy_results("trivy-config.json")

    context = {
        "service_name": "api-gateway",
        "internet_facing": True,
        "handles_sensitive_data": True,
        "base_image": "python:3.12-slim-bookworm",
    }

    prompt = build_analysis_prompt(image_results, context)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
        system="""You are a container security specialist.
Prioritize by real exploitability, not just CVSS.
A critical CVE in a package the application does not use
has lower priority than a high CVE in a library that
processes user input. Be concise and actionable.""",
    )

    report = message.content[0].text
    Path("trivy-analysis.md").write_text(report)
    print(report)

if __name__ == "__main__":
    analyze_trivy_results()