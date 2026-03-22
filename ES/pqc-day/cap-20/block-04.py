# Extraído de: LibroPQC/cap-20-chat-ia.md
@ai_analysis_bp.route('/chat', methods=['POST'])
@jwt_required()
def ai_chat():
    """Chat interactivo con contexto de código"""
    data = request.get_json()
    message = data.get('message', '').strip()
    context = data.get('context', {})
    history = data.get('history', [])
    provider = data.get('provider', 'auto')
    config = data.get('config', {})

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Construir prompt con conocimiento PQC
    system_prompt = _build_chat_system_prompt(context)

    # Ensamblar historial completo
    messages = [{'role': 'system', 'content': system_prompt}]
    for h in history[-20:]:
        messages.append({
            'role': h.get('role', 'user'),
            'content': h.get('content', '')
        })
    messages.append({'role': 'user', 'content': message})

    # Llamar al proveedor de IA
    response_text = _call_ai_chat(messages, provider, config)

    return jsonify({
        'response': response_text,
        'provider': provider,
        'model': config.get('model', 'default')
    }), 200
