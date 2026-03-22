# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
@bp.route('/<int:agent_id>/tools', methods=['PUT'])
@jwt_required()
@require_permission('ai_config.update')
def set_tools(agent_id):
    """Asigna herramientas a un agente validando contra el Tool Registry."""
    agent = AgentDefinition.query.get_or_404(agent_id)
    tools_data = request.get_json().get('tools', [])

    # Validar contra el registry real del AI Service
    ai_service_url = os.environ.get('AI_SERVICE_URL')
    reg_resp = requests.get(f"{ai_service_url}/tools/registry", timeout=5)
    if reg_resp.status_code == 200:
        valid_names = {t['name'] for t in reg_resp.json().get('data', [])}
        invalid = [t['tool_name'] for t in tools_data
                   if t['tool_name'] not in valid_names]
        if invalid:
            return jsonify({
                'success': False,
                'error': f'Herramientas no reconocidas: {", ".join(invalid)}'
            }), 400

    # Reemplazar asignaciones existentes
    AgentToolAssignment.query.filter_by(agent_definition_id=agent_id).delete()
    for i, t in enumerate(tools_data):
        db.session.add(AgentToolAssignment(
            agent_definition_id=agent_id,
            tool_name=t['tool_name'],
            is_enabled=t.get('is_enabled', True),
            sort_order=t.get('sort_order', i),
        ))
    db.session.commit()
