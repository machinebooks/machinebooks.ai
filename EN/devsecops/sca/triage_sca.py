# Source: The DevSecOps and the Machine -- Chapter 5
# Pattern: SCA vulnerability triage with Grype + SBOM context

# scripts/triage_sca.py
"""
Intelligent SCA finding triage.
Receives Grype results + SBOM and prioritizes with Claude.
"""
import json
import sys
import anthropic

def load_results(grype_path: str, sbom_path: str) -> tuple:
    """Load Grype results and SBOM."""
    with open(grype_path) as f:
        vulnerabilities = json.load(f)
    with open(sbom_path) as f:
        sbom = json.load(f)
    return vulnerabilities, sbom

def build_context(vuln: dict, sbom: dict) -> str:
    """Build context for agent analysis."""
    artifact = vuln["artifact"]
    cve = vuln["vulnerability"]

    # Find reverse dependencies in the SBOM
    dependents = find_dependents(artifact["name"], sbom)

    return f"""
## Detected vulnerability

- **CVE**: {cve["id"]}
- **CVSS severity**: {cve["severity"]} ({cve["cvss"][0]["metrics"]["baseScore"]})
- **Package**: {artifact["name"]} v{artifact["version"]}
- **Ecosystem**: {artifact["type"]}
- **Description**: {cve["description"]}
- **Fix available**: {cve["fix"]["state"]} {cve["fix"].get("versions", [])}
- **Declared in**: {artifact["locations"][0]["path"]}
- **Packages depending on this**: {', '.join(dependents) or 'none (direct dependency)'}

## Question
Analyze this vulnerability in context. Consider:
1. Is the affected function used by the application or is it dead code?
2. Does the input that exploits the CVE come from an untrusted external source?
3. Is a fix available and what is the risk of updating?
4. Recommended priority: CRITICAL / HIGH / MEDIUM / LOW / ACCEPT
5. Recommended action: update / mitigate / accept risk / investigate
"""

def find_dependents(package_name: str, sbom: dict) -> list:
    """Find which components depend on the given package."""
    dependents = []
    for dep in sbom.get("dependencies", []):
        if any(package_name in d for d in dep.get("dependsOn", [])):
            dependents.append(dep.get("ref", "unknown"))
    return dependents[:5]  # Limit to 5 to avoid saturating the prompt

def triage_vulnerability(client, vuln: dict, sbom: dict) -> dict:
    """Triage an individual vulnerability with Claude."""
    context = build_context(vuln, sbom)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="""You are a security analyst specializing in SCA.
Your job is to prioritize vulnerabilities in third-party dependencies
considering real exploitability, not just theoretical CVSS.
Respond in JSON with fields: priority, action, reasoning, effort.
Be concise and precise. Do not invent data not in the context.""",
        messages=[{"role": "user", "content": context}]
    )

    return json.loads(message.content[0].text)

def main():
    grype_path = sys.argv[1]
    sbom_path = sys.argv[2]

    client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from environment
    vulnerabilities, sbom = load_results(grype_path, sbom_path)

    results = []
    for match in vulnerabilities.get("matches", []):
        triage = triage_vulnerability(client, match, sbom)
        results.append({
            "cve": match["vulnerability"]["id"],
            "package": match["artifact"]["name"],
            "cvss": match["vulnerability"]["severity"],
            "triage": triage
        })

    # Sort by agent priority, not by CVSS
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "ACCEPT": 4}
    results.sort(key=lambda r: priority_order.get(r["triage"]["priority"], 5))

    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()