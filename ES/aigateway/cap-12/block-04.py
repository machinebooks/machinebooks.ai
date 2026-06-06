# Extraído de: LibroAIGateway/cap-12-cola-rag.md
# gateway/app/api/v1/llm_queued.py:53-54, 152-162
_PRIVILEGED_PURPOSES = ("wizard_full",)
_PRIVILEGED_ROLES = ("admin", "manager")

def _check_purpose_allowed_for_role(purpose, role, is_super):
    if purpose in _PRIVILEGED_PURPOSES and not is_super and role not in _PRIVILEGED_ROLES:
        raise HTTPException(403, f"purpose '{purpose}' requires admin/manager role")
