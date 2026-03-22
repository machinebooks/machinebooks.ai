# Extraído de: LibroTecnico/cap-04-requisito-arquitectura.md
# Fragmento del servicio de IA: streaming de respuesta Claude con SSE
# FastAPI permite async nativo sin configuración adicional

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

app = FastAPI()
client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

async def stream_claude_analysis(document_text: str, context: dict) -> AsyncGenerator[str, None]:
    """
    Genera análisis en streaming desde Claude.
    Cada fragmento se envía como evento SSE al cliente que lo solicita.
    """
    system_prompt = build_analysis_system_prompt(context)

    # claude-sonnet-4-6 para análisis documentales de producción
    # claude-haiku-4-5 para análisis rápidos o resúmenes previos
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Analiza el siguiente documento:\n\n{document_text}"
        }]
    ) as stream:
        async for text_chunk in stream.text_stream:
            # Formato SSE: cada evento es una línea que empieza con "data: "
            yield f"data: {text_chunk}\n\n"

    # Señal de fin del stream
    yield "data: [DONE]\n\n"

@app.post("/analyze/stream")
async def analyze_document_stream(request: AnalysisRequest):
    """Endpoint de análisis con streaming SSE."""
    verify_internal_api_key(request)  # Solo llamadas desde el backend interno

    document_text = await load_document_text(request.doc_id)

    return StreamingResponse(
        stream_claude_analysis(document_text, request.context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Deshabilitar buffering de Nginx para SSE
        }
    )
