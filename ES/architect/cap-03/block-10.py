# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
# Plantilla de equipo: el DAG como diccionario de configuración
# Fichero: ai_service/services/team_executor.py

TEAM_TEMPLATES = {
    "full_bid_preparation": {
        "name": "Preparación Completa de Propuesta",
        "description": "Analiza requisitos, busca equipo, genera propuesta y evalúa",
        "tasks": [
            {"task_id": "analyze_requirements",
             "title": "Análisis de Requisitos",
             "task_type": "analyze_requirements",
             "agent_slug": "analizar_requisitos",
             "depends_on": []},
            {"task_id": "search_team",
             "title": "Búsqueda de Equipo",
             "task_type": "search_cvs",
             "agent_slug": "evaluador_certificaciones",
             "depends_on": ["analyze_requirements"],
             "input_mappings": {
                 "query": "task.analyze_requirements.output.requirements_summary"
             }},
            {"task_id": "search_products",
             "title": "Catálogo de Productos",
             "task_type": "search_products",
             "agent_slug": "catalogo_servicios",
             "depends_on": ["analyze_requirements"],
             "input_mappings": {
                 "query": "task.analyze_requirements.output.technical_scope"
             }},
            {"task_id": "search_references",
             "title": "Proyectos Similares",
             "task_type": "search_projects",
             "agent_slug": "general",
             "depends_on": ["analyze_requirements"],
             "input_mappings": {
                 "query": "task.analyze_requirements.output.scope_summary"
             }},
            {"task_id": "generate_proposal",
             "title": "Generación de Propuesta Técnica",
             "task_type": "generate_proposal",
             "agent_slug": "generador_propuestas",
             "depends_on": ["analyze_requirements", "search_team",
                            "search_products", "search_references"],
             "input_mappings": {
                 "requirements": "task.analyze_requirements.output.requirements",
                 "team_profiles": "task.search_team.output.profiles",
                 "products": "task.search_products.output.results",
                 "references": "task.search_references.output.results"
             }},
            {"task_id": "evaluate_proposal",
             "title": "Evaluación de la Propuesta",
             "task_type": "evaluate_proposal",
             "agent_slug": "evaluador_respuestas",
             "depends_on": ["generate_proposal"],
             "input_mappings": {
                 "proposal_content": "task.generate_proposal.output.content"
             }},
        ],
    },
}
