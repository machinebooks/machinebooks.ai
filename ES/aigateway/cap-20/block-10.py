# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/firewall_service.py:143-165

def _pick_override(overrides: list[dict], *, target_type: str,
                   target_key: str, org_id, team_id, user_id) -> Optional[str]:
    """Resuelve el override más específico: user > team > org."""
    for scope_type, scope_id in (("user", user_id), ("team", team_id), ("org", org_id)):
        if scope_id is None:
            continue
        for ov in overrides:
            if (
                ov.get("scope_type") == scope_type
                and ov.get("scope_id") == scope_id
                and ov.get("target_type") == target_type
                and str(ov.get("target_key")) == str(target_key)
                and ov.get("action") in _VALID_ACTIONS
            ):
                return ov["action"]
    return None
