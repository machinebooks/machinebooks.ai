# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
# Configuración de acceso RAG por colección
# REGLA: cualquier colección no listada aquí es SYSTEM_ONLY por defecto
RAG_COLLECTION_ACCESS = {
    # Colecciones públicas — accesibles por cualquier usuario autenticado
    "knowledge_base": {"access": "authenticated",
                       "description": "Base de conocimiento general"},
    "help_center":    {"access": "authenticated",
                       "description": "Centro de ayuda"},

    # Colecciones restringidas — requieren permiso explícito en AppRole
    "commercial_catalog":   {"access": "restricted",
                              "required_permission": "catalog.read"},
    "historical_proposals": {"access": "restricted",
                              "required_permission": "proposals.read"},
    "client_documents":     {"access": "restricted",
                              "required_permission": "clients.read"},

    # Colecciones system-only — solo accesibles por servicios internos
    "opportunities_feed":  {"access": "system_only",
                             "description": "3.8M vectores de oportunidades"},
    "internal_analytics":  {"access": "system_only",
                             "description": "Datos analíticos agregados"},
}

def check_rag_collection_access(user_id, app_code, collection_name):
    """Verifica si el usuario puede consultar una colección RAG específica.
    DEFAULT DENY: colecciones desconocidas son siempre system_only."""
    config = RAG_COLLECTION_ACCESS.get(collection_name)
    if not config:
        # Colección desconocida — denegar y auditar
        audit_log('ACCESS_DENIED', severity='WARNING',
                 details=f"Colección RAG no registrada: {collection_name}")
        return False  # Default deny — nunca default allow

    if config["access"] == "authenticated":
        return True  # Cualquier usuario autenticado

    if config["access"] == "system_only":
        # Solo API keys internas, nunca usuarios directos
        return g.get('is_service_call', False)

    if config["access"] == "restricted":
        permissions = get_user_permissions(user_id, app_code)
        module, action = config["required_permission"].split(".")
        return action in permissions.get(module, [])

    return False  # Default deny para configuraciones no reconocidas
