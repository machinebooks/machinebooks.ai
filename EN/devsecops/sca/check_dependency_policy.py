# Source: The DevSecOps and the Machine -- Chapter 5
# Pattern: Dependency policy enforcement (licenses, vulnerabilities)

# scripts/check_dependency_policy.py
"""
Validate SBOM and Grype findings against the dependency policy.
Returns exit code 1 if any blocking rule is violated.
"""
import json
import sys
import yaml
from datetime import datetime, timedelta

def load_policy(policy_path: str) -> dict:
    with open(policy_path) as f:
        return yaml.safe_load(f)["policy"]

def check_licenses(sbom: dict, policy: dict) -> list:
    """Verify each component's licenses against the policy."""
    violations = []
    blocked = set(policy["licenses"]["blocked"])
    review = set(policy["licenses"]["review_required"])

    for comp in sbom.get("components", []):
        for lic in comp.get("licenses", []):
            lic_id = lic.get("license", {}).get("id", "")
            if lic_id in blocked:
                violations.append({
                    "type": "license_blocked",
                    "severity": "critical",
                    "package": comp["name"],
                    "license": lic_id,
                    "message": f"{comp['name']} uses blocked license: {lic_id}"
                })
            elif lic_id in review:
                violations.append({
                    "type": "license_review",
                    "severity": "warning",
                    "package": comp["name"],
                    "license": lic_id,
                    "message": f"{comp['name']} uses license requiring review: {lic_id}"
                })

    # Check components without license
    if policy.get("supply_chain", {}).get("require_known_license"):
        for comp in sbom.get("components", []):
            if not comp.get("licenses"):
                violations.append({
                    "type": "no_license",
                    "severity": "warning",
                    "package": comp["name"],
                    "message": f"{comp['name']} does not declare a license"
                })

    return violations

def check_vulnerabilities(vulns: dict, policy: dict) -> list:
    """Verify vulnerabilities against policy thresholds."""
    violations = []

    for rule in policy["vulnerabilities"]["block_on"]:
        for match in vulns.get("matches", []):
            sev = match["vulnerability"]["severity"].lower()
            if sev == rule["severity"]:
                violations.append({
                    "type": "vulnerability_blocked",
                    "severity": "critical",
                    "cve": match["vulnerability"]["id"],
                    "package": match["artifact"]["name"],
                    "message": (
                        f"{match['vulnerability']['id']} ({sev}) in "
                        f"{match['artifact']['name']} — blocked by policy"
                    )
                })

    return violations

def main():
    policy = load_policy(".github/dependency-policy.yml")

    with open(sys.argv[1]) as f:  # sbom.cdx.json
        sbom = json.load(f)
    with open(sys.argv[2]) as f:  # grype-results.json
        vulns = json.load(f)

    violations = []
    violations.extend(check_licenses(sbom, policy))
    violations.extend(check_vulnerabilities(vulns, policy))

    critical_violations = [v for v in violations if v["severity"] == "critical"]

    for v in violations:
        prefix = "BLOCK" if v["severity"] == "critical" else "WARN"
        print(f"[{prefix}] {v['message']}")

    if critical_violations:
        print(f"\n{len(critical_violations)} blocking policy violations.")
        sys.exit(1)
    else:
        print(f"\n{len(violations)} warnings, 0 blocks. Pipeline approved.")

if __name__ == "__main__":
    main()