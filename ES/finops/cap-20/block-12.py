# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# Validador que distingue parámetros bloqueados de sobreescribibles
LOCKED_PARAMS = [
    "throttling.requests_per_day_global_limit",
    "model_routing.forbidden_models",
    "fallback.on_exhaustion",
]

def validate_override_permissions(
    override: dict, tenant_tier: str
) -> list:
    """Verifica que el override no toca parámetros bloqueados."""
    violations = []
    for locked in LOCKED_PARAMS:
        keys = locked.split(".")
        current = override
        for key in keys:
            if isinstance(current, dict) and key in current:
                violations.append({
                    "param": locked,
                    "error": f"'{locked}' está bloqueado.",
                })
                break
            current = (
                current.get(key, {})
                if isinstance(current, dict) else {}
            )
    return violations
