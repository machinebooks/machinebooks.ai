# Extraído de: LibroPQC/cap-20-chat-ia.md
@ai_analysis_bp.route('/chat/agent', methods=['POST'])
@jwt_required()
def ai_chat_agent():
    """Modo agente: exploración autónoma de repositorios"""
    data = request.get_json()
    message = data.get('message', '').strip()
    repo_path = data.get('repo_path', '')
    history = data.get('history', [])
    provider = data.get('provider', 'auto')
    config = data.get('config', {})
    stream = data.get('stream', False)

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({'error': 'Repository path required'}), 400

    # Crear agente con herramientas de repositorio
    agent = CodeAnalysisAgent(repo_path, provider, config)

    if stream:
        # SSE: emitir eventos en tiempo real
        def generate():
            for event in agent.run(message, history):
                yield f"data: {json.dumps(event)}\n\n"
            yield "data: [DONE]\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        # Síncrono: devolver resultado completo
        result = agent.run_sync(message, history)
        return jsonify({
            'response': result['response'],
            'actions': result['actions'],
            'iterations': result['iterations'],
            'events': result.get('events', [])
        }), 200
