# Extraído de: LibroTecnico/cap-08-colas-trabajo.md
# Ejemplo didáctico: routing centralizado de tareas
# Patrón: workers/celery_routing.py

CELERY_ROUTES = {
    # Tareas de IA → cola ai (worker ai)
    "tasks.ai.analyze_document":       {"queue": "ai"},
    "tasks.ai.generate_proposal":      {"queue": "ai"},
    "tasks.ai.analyze_cv":             {"queue": "ai"},
    "tasks.ai.score_opportunity":      {"queue": "ai"},
    "tasks.ai.compliance_check":       {"queue": "ai"},

    # Procesamiento de documentos → cola documents (worker ai)
    "tasks.documents.process_upload":  {"queue": "documents"},
    "tasks.documents.index_vectors":   {"queue": "documents"},
    "tasks.documents.reindex_rag":     {"queue": "documents"},

    # Automatización RPA → cola automation (worker automation)
    "tasks.automation.crm_bot":        {"queue": "automation"},
    "tasks.automation.portal_bot":     {"queue": "automation"},
    "tasks.automation.pricing_bot":    {"queue": "automation"},
    "tasks.automation.reporting_bot":  {"queue": "automation"},

    # Sincronización CRM → cola crm (worker default)
    "tasks.sync.crm_opportunities":    {"queue": "crm"},
    "tasks.sync.crm_accounts":         {"queue": "crm"},

    # Sincronización genérica → cola sync (worker default)
    "tasks.sync.meilisearch_reindex":  {"queue": "sync"},
    "tasks.sync.gdpr_cleanup":         {"queue": "sync"},

    # Alertas críticas → cola priority (worker default)
    "tasks.alerts.proactive_scan":     {"queue": "priority"},
    "tasks.alerts.compliance_alert":   {"queue": "priority"},
}
