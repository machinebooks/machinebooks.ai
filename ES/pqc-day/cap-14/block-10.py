# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
@ai_admin_bp.route('/providers/<int:provider_id>/test', methods=['POST'])
@jwt_required()
def test_provider(provider_id):
    """Ejecuta un test de conectividad contra el proveedor LLM
    y registra latencia, estado y mensaje de resultado."""
    provider = AIProvider.query.get_or_404(provider_id)
    start = time.time()
    try:
        result = ai_service.test_provider_connection(provider)
        latency_ms = int((time.time() - start) * 1000)
        provider.last_test_at = datetime.utcnow()
        provider.last_test_status = (
            'success' if result['success'] else 'failure')
        provider.last_test_latency_ms = latency_ms
        db.session.commit()
        return jsonify({
            'success': result['success'],
            'latency_ms': latency_ms
        })
    except Exception as e:
        provider.last_test_status = 'failure'
        provider.last_test_message = str(e)
        db.session.commit()
        return jsonify({'success': False, 'message': str(e)}), 500
