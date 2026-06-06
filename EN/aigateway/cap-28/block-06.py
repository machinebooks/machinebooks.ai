# Extracted from: LibroAIGateway/cap-28-admin-operations-ai.md
# gateway/app/api/v1/admin/dashboard.py:15-20 (filtering pattern)
def _apply_org_filter(query, model, current_user):
    """Applies multi-tenant filter to any SQLAlchemy query."""
    ids = org_filter_ids(current_user)  # None = superadmin (sees everything)
    if ids is not None:
        query = query.where(model.organization_id.in_(ids))
    return query
