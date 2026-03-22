# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
# Estructura de un caso de prueba registrado en la definición del agente
{
    "test_case_id": "tc_001",
    "description": "Consulta típica de búsqueda de oportunidades",
    "input": "Busca oportunidades en el sector energía con presupuesto mayor de 500.000 euros",
    "expected_tools": ["search_opportunities"],
    "expected_stop_reason": "end_turn",
    "max_iterations_allowed": 3,
    "guardrail_should_not_trigger": True
}
