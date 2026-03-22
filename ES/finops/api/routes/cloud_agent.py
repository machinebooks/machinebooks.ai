# Extraído de: LibroFinOps/cap-12-agente-coste-cloud.md
# api/routes/cloud_agent.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from cloud_cost_agent.agent import run_cost_agent
import time

router = APIRouter(prefix="/cloud-agent", tags=["Cloud Cost Agent"])


class AgentQuery(BaseModel):
    question: str
    context: dict | None = None  # Contexto adicional: presupuesto, equipo, etc.


class AgentResponse(BaseModel):
    answer: str
    execution_time_seconds: float
    tools_called: int  # Para métricas de uso


@router.post("/query", response_model=AgentResponse)
async def query_cloud_costs(query: AgentQuery) -> AgentResponse:
    """
    Consulta el agente de costes cloud en lenguaje natural.
    El agente decide qué APIs cloud consultar y cómo agregar los resultados.
    """
    start_time = time.time()

    try:
        # Enriquecemos la pregunta con contexto si lo hay
        full_question = query.question
        if query.context:
            context_str = "\n".join(
                f"- {k}: {v}" for k, v in query.context.items()
            )
            full_question = (
                f"Contexto adicional:\n{context_str}\n\n"
                f"Pregunta: {query.question}"
            )

        answer = await run_cost_agent(full_question)

        return AgentResponse(
            answer=answer,
            execution_time_seconds=round(time.time() - start_time, 2),
            tools_called=0  # En producción: instrumentar el ciclo del agente
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el agente de costes: {str(e)}"
        )
