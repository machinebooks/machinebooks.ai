# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/agent.py

import anthropic
from agents import Agent, Runner

compliance_agent = Agent(
    name="ComplianceAgent",
    model="claude-sonnet-4-6",
    instructions="""
    Eres un agente especializado en cumplimiento normativo.
    Tu función es analizar el estado de cumplimiento de los marcos
    regulatorios y estándares configurados en la Plataforma.

    REGLAS:
    - Siempre basa tus respuestas en datos reales del sistema.
    - Nunca inventes estados de cumplimiento ni evidencias.
    - Cuando identifiques gaps, sugiere acciones concretas.
    - Si no tienes datos suficientes, dilo explícitamente.
    - La suficiencia de una evidencia es juicio del auditor humano.
      Tú identificas gaps cuantitativos, no evalúas calidad.
    """,
    tools=[
        evaluate_control_gap,
        generate_soa_tool,
        get_cross_framework_status
    ]
)

async def analyze_compliance_status(
    query: str,
    tenant_id: int,
    db: Session,
    rag_service = None
) -> str:
    """
    Punto de entrada del agente de compliance.
    Recibe una consulta en lenguaje natural y devuelve
    un análisis basado en datos reales del sistema.
    """
    result = await Runner.run(
        compliance_agent,
        input=query,
        context={
            "db": db,
            "tenant_id": tenant_id,
            "rag_service": rag_service
        }
    )
    return result.final_output
