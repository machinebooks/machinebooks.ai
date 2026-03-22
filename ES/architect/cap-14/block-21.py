# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
@bp.route('/internal/<slug>', methods=['GET'])
def internal_get_by_slug(slug):
    """Endpoint interno: el AI Service consulta la definición por slug."""
    if not _verify_internal_key():
        return jsonify({'error': 'Unauthorized'}), 401
    agent = AgentDefinition.query.filter_by(slug=slug, is_active=True).first()
    if not agent:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'success': True,
        'data': agent.to_dict(include_tools=True, include_guardrails=True),
    })
