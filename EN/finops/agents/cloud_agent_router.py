# Source: The FinOps Engineer and the Machine -- Chapter 12
# Pattern: FastAPI router for cloud agent queries

# api/routes/cloud_agent.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from cloud_cost_agent.agent import run_cost_agent
import time

router = APIRouter(prefix="/cloud-agent", tags=["Cloud Cost Agent"])


class AgentQuery(BaseModel):
    question: str
    context: dict | None = None  # Additional context: budget, team, etc.


class AgentResponse(BaseModel):
    answer: str
    execution_time_seconds: float
    tools_called: int  # For usage metrics


@router.post("/query", response_model=AgentResponse)
async def query_cloud_costs(query: AgentQuery) -> AgentResponse:
    """
    Queries the cloud cost agent in natural language.
    The agent decides which cloud APIs to query and how to aggregate results.
    """
    start_time = time.time()

    try:
        # Enrich the question with context if available
        full_question = query.question
        if query.context:
            context_str = "\n".join(
                f"- {k}: {v}" for k, v in query.context.items()
            )
            full_question = (
                f"Additional context:\n{context_str}\n\n"
                f"Question: {query.question}"
            )

        answer = await run_cost_agent(full_question)

        return AgentResponse(
            answer=answer,
            execution_time_seconds=round(time.time() - start_time, 2),
            tools_called=0  # In production: instrument the agent cycle
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cost agent error: {str(e)}"
        )
