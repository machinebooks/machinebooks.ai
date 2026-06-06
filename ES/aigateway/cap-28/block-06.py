# Extraído de: LibroAIGateway/cap-28-admin-operaciones-ia.md
# gateway/app/api/v1/admin/dashboard.py:15-20 (patrón de filtrado)
def _apply_org_filter(query, model, current_user):
    """Aplica filtro multi-tenant a cualquier consulta SQLAlchemy."""
    ids = org_filter_ids(current_user)  # None = superadmin (ve todo)
    if ids is not None:
        query = query.where(model.organization_id.in_(ids))
    return query
