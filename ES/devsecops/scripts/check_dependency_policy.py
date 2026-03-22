# Extraído de: LibroDevSecOps/cap-05-sca-sbom.md
# scripts/check_dependency_policy.py
"""
Valida el SBOM y los hallazgos de Grype contra la política de dependencias.
Devuelve exit code 1 si alguna regla de bloqueo se incumple.
"""
import json
import sys
import yaml
from datetime import datetime, timedelta

def load_policy(policy_path: str) -> dict:
    with open(policy_path) as f:
        return yaml.safe_load(f)["policy"]

def check_licenses(sbom: dict, policy: dict) -> list:
    """Verifica licencias de cada componente contra la política."""
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
                    "message": f"{comp['name']} usa licencia bloqueada: {lic_id}"
                })
            elif lic_id in review:
                violations.append({
                    "type": "license_review",
                    "severity": "warning",
                    "package": comp["name"],
                    "license": lic_id,
                    "message": f"{comp['name']} usa licencia que requiere revisión: {lic_id}"
                })

    # Verificar componentes sin licencia
    if policy.get("supply_chain", {}).get("require_known_license"):
        for comp in sbom.get("components", []):
            if not comp.get("licenses"):
                violations.append({
                    "type": "no_license",
                    "severity": "warning",
                    "package": comp["name"],
                    "message": f"{comp['name']} no declara licencia"
                })

    return violations

def check_vulnerabilities(vulns: dict, policy: dict) -> list:
    """Verifica vulnerabilidades contra umbrales de la política."""
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
                        f"{match['vulnerability']['id']} ({sev}) en "
                        f"{match['artifact']['name']} — bloqueo por política"
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
        print(f"\n{len(critical_violations)} violaciones de política bloqueantes.")
        sys.exit(1)
    else:
        print(f"\n{len(violations)} avisos, 0 bloqueos. Pipeline aprobado.")

if __name__ == "__main__":
    main()
