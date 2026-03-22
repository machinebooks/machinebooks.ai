# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
TEAM_TEMPLATES = {
    "full_bid_preparation": {
        "name": "Preparación Completa de Propuesta",
        "description": "Analiza requisitos, busca equipo, genera propuesta y evalúa",
        "tasks": [
            {
                "task_id": "analyze_requirements",
                "title": "Análisis de Requisitos",
                "task_type": "analyze_requirements",
                "agent_slug": "analizar_requisitos",
                "depends_on": [],           # Sin dependencias: se ejecuta primero
            },
            {
                "task_id": "search_team",
                "title": "Búsqueda de Equipo",
                "task_type": "search_cvs",
                "agent_slug": "perfiles_certificaciones",
                "depends_on": ["analyze_requirements"],
                "input_mappings": {
                    "query": "task.analyze_requirements.output.requirements_summary"
                },
            },
            {
                "task_id": "search_products",
                "title": "Catálogo de Productos",
                "task_type": "search_products",
                "agent_slug": "experto_catalogo",
                "depends_on": ["analyze_requirements"],
                # search_team y search_products corren EN PARALELO
            },
            {
                "task_id": "generate_offer",
                "title": "Generación de Propuesta Técnica",
                "agent_slug": "generador_propuestas",
                "depends_on": ["analyze_requirements", "search_team",
                               "search_products", "search_references"],
                # Espera a que TODAS las búsquedas terminen
            },
        ],
    },
}
