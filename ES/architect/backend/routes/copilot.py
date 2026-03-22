# Extraído de: LibroTecnico/cap-07-api-rest.md
# backend/routes/copilot.py (versión refactorizada)
from flask import Blueprint, request, jsonify, g, Response
from middleware.auth import platform_guard, require_permission
from middleware.rate_limit import rate_limit
from services.copilot_orchestrator import CopilotOrchestrator
from services.guardrail_service import GuardrailService
import json

copilot_bp = Blueprint('copilot', __name__, url_prefix='/api/copilot')

@copilot_bp.route('/chat', methods=['POST'])
@platform_guard
@require_permission('copilot', 'use')
@rate_limit(max_requests=10, window_seconds=60, key_prefix="copilot_chat")
def chat():
    """Endpoint principal del copilot. Soporta streaming SSE.
    El modo de agente se determina automáticamente por el clasificador de intención."""
    data = request.get_json()
    message = data.get('message', '').strip()
    if len(message) > 10000:
        return jsonify({'error': 'Mensaje demasiado largo'}), 400
    session_id = data.get('session_id')
    mode = data.get('mode', 'auto')  # auto | chat_rag | agent_tools | orchestrate

    if not message:
        return jsonify({'error': 'Mensaje requerido'}), 400

    # Verificar guardrails de entrada antes de llamar al servicio IA
    guardrail_result = GuardrailService.check_input(
        message=message,
        user_id=g.current_user.id,
        context={'app': g.current_app_code}
    )

    if guardrail_result.action == 'BLOCK':
        # El mensaje fue bloqueado por los guardrails — no llamar al modelo
        return jsonify({
            'error': 'Mensaje no permitido',
            'reason': guardrail_result.reason
        }), 400

    # Si el cliente soporta SSE, usar streaming; si no, respuesta síncrona
    accept_header = request.headers.get('Accept', '')
    use_streaming = 'text/event-stream' in accept_header

    if use_streaming:
        return Response(
            _stream_response(message, session_id, mode, guardrail_result),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'  # Necesario para Nginx con SSE
            }
        )
    else:
        # Respuesta síncrona para clientes que no soportan SSE
        orchestrator = CopilotOrchestrator(g.current_user, session_id)
        result = orchestrator.process(message, mode=mode)
        return jsonify(result)


def _stream_response(message, session_id, mode, guardrail_input):
    """Generador de eventos SSE para streaming de respuesta del agente."""
    try:
        orchestrator = CopilotOrchestrator(g.current_user, session_id)
        for chunk in orchestrator.stream(message, mode=mode):
            # Verificar guardrails en cada fragmento de respuesta
            if GuardrailService.check_output_chunk(chunk).action == 'BLOCK':
                yield f"data: {json.dumps({'type': 'error', 'content': 'Respuesta filtrada'})}\n\n"
                return
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        logger.error("copilot_stream_failed",
                     request_id=g.request_id,
                     error=str(e))
        yield f"data: {json.dumps({'type': 'error', 'content': 'Error en el procesamiento'})}\n\n"
