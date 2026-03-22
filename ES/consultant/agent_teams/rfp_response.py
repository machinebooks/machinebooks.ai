# Extraído de: LibroConsultor/cap-07-claude-code-consultoria.md
# agent_teams/rfp_response.py
from claude_agent_sdk import Agent, tool, orchestrator

# Agente coordinador — gestiona el flujo global
coordinator = Agent(
    name="rfp-coordinator",
    model="claude-sonnet-4-6",
    system="""Coordinas la respuesta a un RFP. Tu trabajo:
    1. Distribuir secciones del pliego a agentes especializados
    2. Integrar sus análisis en una visión coherente
    3. Identificar contradicciones entre requisitos
    4. Producir la recomendación go/no-go consolidada"""
)

# Agente de análisis técnico
tech_analyst = Agent(
    name="tech-analyst",
    model="claude-sonnet-4-6",
    system="""Analizas requisitos técnicos de RFPs:
    - Arquitectura exigida, tecnologías, integraciones
    - Viabilidad técnica con nuestro stack actual
    - Riesgos técnicos y mitigaciones
    - Esfuerzo de implementación (jornadas por componente)"""
)

# Agente de cumplimiento normativo
compliance_analyst = Agent(
    name="compliance-analyst",
    model="claude-sonnet-4-6",
    system="""Verificas requisitos de cumplimiento en RFPs:
    - Frameworks normativos exigidos (ISO, ENS, NIS2, DORA)
    - Certificaciones requeridas del equipo
    - Requisitos de confidencialidad y protección de datos
    - Cláusulas de penalización y SLAs"""
)

# Agente de estimación financiera
financial_analyst = Agent(
    name="financial-analyst",
    model="claude-haiku-4-5",
    system="""Estimas el impacto financiero de propuestas:
    - Coste de equipo basado en perfiles y dedicación
    - Costes de herramientas y licencias
    - Margen objetivo y precio competitivo
    - Comparativa con proyectos similares"""
)

@orchestrator(agents=[coordinator, tech_analyst,
                       compliance_analyst, financial_analyst])
async def analyze_rfp_complete(rfp_content: str) -> dict:
    """Flujo completo de análisis de RFP con equipo de agentes."""
    # 1. El coordinador segmenta el pliego
    segments = await coordinator.run(
        f"Segmenta este RFP en bloques temáticos:\n{rfp_content}"
    )
    # 2. Cada agente analiza su segmento en paralelo
    tech_result = await tech_analyst.run(
        f"Analiza los requisitos técnicos:\n{segments['technical']}"
    )
    compliance_result = await compliance_analyst.run(
        f"Verifica cumplimiento normativo:\n{segments['compliance']}"
    )
    financial_result = await financial_analyst.run(
        f"Estima impacto financiero:\n{segments['financial']}"
    )
    # 3. El coordinador consolida
    consolidated = await coordinator.run(
        f"""Consolida estos análisis en recomendación go/no-go:
        Técnico: {tech_result}
        Cumplimiento: {compliance_result}
        Financiero: {financial_result}"""
    )
    return consolidated
