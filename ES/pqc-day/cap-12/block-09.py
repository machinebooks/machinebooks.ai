# Extraído de: LibroPQC/cap-12-agente-autonomo.md
@ai_analysis_bp.route('/chat/agent', methods=['POST'])
@jwt_required()
def ai_chat_agent():
    """
    POST /api/ai/chat/agent
    Body: {
        "message": "Analiza la postura criptográfica de este repositorio",
        "repo_path": "/tmp/pqc_repo_cache/owner/repo",
        "provider": "anthropic",
        "config": {"model": "claude-sonnet-4-6"},
        "stream": true
    }
    """
    data = request.get_json()
    message = data.get('message', '')
    repo_path = data.get('repo_path', '')
    provider = data.get('provider', 'auto')
    config = data.get('config', {})
    stream = data.get('stream', False)

    # Validar que el repositorio existe
    if not os.path.exists(repo_path):
        return jsonify({'error': 'Repositorio no encontrado'}), 404

    # Crear instancia del agente
    agent = CodeAnalysisAgent(repo_path, provider, config)

    if stream:
        # Streaming: generador SSE
        def generate():
            for event in agent.run(message, data.get('history', [])):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'  # Evitar buffering en Nginx
            }
        )
    else:
        # Síncrono: resultado completo
        result = agent.run_sync(message, data.get('history', []))
        return jsonify(result)
