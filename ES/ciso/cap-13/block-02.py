# Extraído de: LibroCISO/cap-13-orquestador-copiloto.md
# Ejemplo didáctico: patrones/api/copilot_endpoint.py

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import json

router = APIRouter(prefix="/api/v1/copilot", tags=["copilot"])

@router.post("/chat")
async def copilot_chat(
    payload: CopilotChatPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint principal del copiloto.
    Devuelve un stream SSE con eventos de ejecución en tiempo real.
    """
    request = CopilotRequest(
        message=payload.message,
        session_id=payload.session_id,
        user_id=str(current_user.id),
        module_context=payload.module_context,
        tenant_id=str(current_user.corporate_id),  # Multi-tenancy
    )

    orchestrator = get_copilot_orchestrator()  # Singleton inyectado

    async def event_generator():
        async for event in orchestrator.process(request):
            event_type = event.pop("type", "message")
            yield {
                "event": event_type,
                "data": json.dumps(event, ensure_ascii=False)
            }

    return EventSourceResponse(event_generator())
