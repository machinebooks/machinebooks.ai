# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
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
    Analiza un plan de Terraform en formato JSON y verifica
    que todos los recursos nuevos o modificados tengan las etiquetas obligatorias.
    Devuelve lista de violaciones encontradas.
    """
    with open(plan_file) as f:
        plan = json.load(f)

    violations = []

    for change in plan.get("resource_changes", []):
        # Solo revisar recursos que se van a crear o actualizar
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
                    "violation": f"Falta la etiqueta obligatoria: {required_tag}",
                    "severity": "error",
                })
            elif required_tag in ALLOWED_VALUES:
                value = tags[required_tag]
                if value not in ALLOWED_VALUES[required_tag]:
                    violations.append({
                        "resource": f"{resource_type}.{resource_name}",
                        "violation": (
                            f"Valor inválido para '{required_tag}': '{value}'. "
                            f"Valores permitidos: {sorted(ALLOWED_VALUES[required_tag])}"
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
        print(f"\n{len(errors)} error(es) de tagging. El despliegue está bloqueado.")
        sys.exit(1)  # Falla el pipeline

    print(f"\nValidación de tags: {len(warnings)} advertencias. Despliegue permitido.")
    sys.exit(0)
