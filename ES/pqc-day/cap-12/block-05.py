# Extraído de: LibroPQC/cap-12-agente-autonomo.md
def _call_anthropic(self, messages: list, model: str, timeout: int) -> dict:
    """Llamada a Claude con conversión de formato de herramientas."""
    # Separar system message (Claude lo requiere aparte)
    system_msg = ""
    formatted = []
    for msg in messages:
        if msg['role'] == 'system':
            system_msg = msg['content']
        elif msg['role'] == 'tool':
            # Claude espera tool_result como contenido del rol 'user'
            formatted.append({
                'role': 'user',
                'content': [{
                    'type': 'tool_result',
                    'tool_use_id': msg.get('tool_call_id', ''),
                    'content': msg.get('content', '')
                }]
            })
        else:
            formatted.append({'role': msg['role'], 'content': msg['content']})

    # Convertir herramientas al formato Anthropic
    anthropic_tools = [{
        'name': t['function']['name'],
        'description': t['function']['description'],
        'input_schema': t['function']['parameters']
    } for t in self.tool_definitions]

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        },
        json={
            'model': model or 'claude-sonnet-4-6',
            'max_tokens': 4096,
            'system': system_msg,
            'messages': formatted,
            'tools': anthropic_tools,
            'tool_choice': {'type': 'auto'}
        },
        timeout=timeout
    )

    # Parsear respuesta: extraer texto y tool_use blocks
    data = response.json()
    text = ""
    tool_calls = []
    for block in data.get('content', []):
        if block['type'] == 'text':
            text += block['text']
        elif block['type'] == 'tool_use':
            tool_calls.append({
                'id': block['id'],
                'name': block['name'],
                'arguments': block['input']
            })

    return {'content': text, 'tool_calls': tool_calls}
