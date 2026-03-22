# Source: The FinOps Engineer and the Machine -- Chapter 5
# Pattern: Terraform tag validation script

# scripts/validate_terraform_tags.py
import json
import sys

REQUIRED_TAGS = ["environment", "team", "service", "cost-center"]
ALLOWED_VALUES = {
    "environment": {"prod", "staging", "dev", "sandbox"},
    "team": {"backend", "frontend", "data", "platform", "security"},
}

def validate_terraform_plan(plan_file: str) -> list[dict]:
    """
    Analyzes a Terraform plan in JSON format and verifies
    that all new or modified resources have the mandatory tags.
    Returns a list of violations found.
    """
    with open(plan_file) as f:
        plan = json.load(f)

    violations = []

    for change in plan.get("resource_changes", []):
        # Only check resources being created or updated
        if change["change"]["actions"] not in [["create"], ["update"], ["create", "delete"]]:
            continue

        after = change["change"].get("after", {})
        tags = after.get("tags", {}) or after.get("labels", {})

        resource_type = change["type"]
        resource_name = change["name"]

        for required_tag in REQUIRED_TAGS:
            if required_tag not in tags:
                violations.append({
                    "resource": f"{resource_type}.{resource_name}",
                    "violation": f"Missing mandatory tag: {required_tag}",
                    "severity": "error",
                })
            elif required_tag in ALLOWED_VALUES:
                value = tags[required_tag]
                if value not in ALLOWED_VALUES[required_tag]:
                    violations.append({
                        "resource": f"{resource_type}.{resource_name}",
                        "violation": (
                            f"Invalid value for '{required_tag}': '{value}'. "
                            f"Allowed values: {sorted(ALLOWED_VALUES[required_tag])}"
                        ),
                        "severity": "warning",
                    })

    return violations


if __name__ == "__main__":
    plan_file = sys.argv[1] if len(sys.argv) > 1 else "tfplan.json"
    violations = validate_terraform_plan(plan_file)

    errors = [v for v in violations if v["severity"] == "error"]
    warnings = [v for v in violations if v["severity"] == "warning"]

    for v in violations:
        prefix = "ERROR" if v["severity"] == "error" else "WARN"
        print(f"[{prefix}] {v['resource']}: {v['violation']}")

    if errors:
        print(f"\n{len(errors)} tagging error(s). Deployment is blocked.")
        sys.exit(1)  # Fail the pipeline

    print(f"\nTag validation: {len(warnings)} warning(s). Deployment permitted.")
    sys.exit(0)
