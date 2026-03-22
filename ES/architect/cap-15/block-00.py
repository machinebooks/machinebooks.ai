# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import anthropic
import json
from typing import AsyncGenerator

client = anthropic.AsyncAnthropic()

async def stream_claude_response(
    messages: list[dict],
    system_prompt: str,
    model: str = "claude-sonnet-4-6"
) -> AsyncGenerator[str, None]:
    """
    Generador asíncrono que emite tokens de Claude como eventos SSE.
    Cada token se emite inmediatamente para minimizar latencia percibida.
    """
    async with client.messages.stream(
        model=model,
        max_tokens=2048,
        system=system_prompt,
        messages=messages
    ) as stream:
        async for text in stream.text_stream:
            # Formato SSE: cada chunk es un evento 'delta'
            yield json.dumps({"type": "delta", "content": text})

        # Evento final con metadatos de uso (tokens, coste)
        usage = await stream.get_final_usage()
        yield json.dumps({
            "type": "done",
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens
        })

@app.post("/chat/stream")
async def chat_stream(
    request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """
    Endpoint de chat con streaming SSE.
    Construye contexto con User Memory antes de llamar a Claude.
    """
    body = await request.json()
    message = body["message"]
    conversation_history = body.get("history", [])
    chat_context = body.get("context", {})  # tipo de chat, doc_id, etc.

    # 1. Cargar memorias del usuario (top 10 más relevantes)
    user_memories = await load_user_memories(user_id, limit=10)

    # 2. Construir system prompt con contexto y memorias
    system_prompt = build_system_prompt(
        base_context=chat_context,
        memories=user_memories
    )

    # 3. Preparar historial con el nuevo mensaje
    messages = conversation_history + [
        {"role": "user", "content": message}
    ]

    # 4. Streaming como EventSourceResponse
    return EventSourceResponse(
        stream_claude_response(messages, system_prompt),
        media_type="text/event-stream"
    )
