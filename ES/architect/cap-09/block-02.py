# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: lanzamiento del análisis de documentos
# Patrón: backend/routes/documents/analysis_routes.py

@documents_bp.route("/documents/<int:doc_id>/analyze", methods=["POST"])
@platform_guard
@require_permission("documents", "analyze")
def launch_analysis(doc_id: int):
    """
    Lanza el análisis IA de un documento.
    El procesamiento es asíncrono; el cliente consulta el estado vía polling.
    """
    document = Document.query.get_or_404(doc_id)

    # Evitar análisis duplicados concurrentes
    if document.analysis_status in ("processing", "pending"):
        return jsonify({"error": "Análisis ya en curso"}), 409

    document.analysis_status = "pending"
    db.session.commit()

    # Enviar al worker de IA con prioridad según tipo de documento
    task = celery_app.send_task(
        "tasks.ai.analyze_document",
        args=[doc_id],
        kwargs={
            "model": "claude-opus-4-6",
            "analysis_type": document.doc_type,
            "user_id": g.current_user.id,
        },
        queue="ai",
        priority=8 if document.doc_type == "requirements" else 5
    )

    document.celery_task_id = task.id
    db.session.commit()

    return jsonify({
        "status": "queued",
        "task_id": task.id,
        "polling_url": f"/api/documents/{doc_id}/analysis/status"
    }), 202
