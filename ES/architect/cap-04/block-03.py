# Extraído de: LibroTecnico/cap-04-requisito-arquitectura.md
# Patrón de comunicación backend → ai_service a través de Celery
# El backend delega operaciones de IA sin bloquear la API REST

import os
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from celery_app import celery

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/api/documents/<int:doc_id>/analyze", methods=["POST"])
@jwt_required()
def analyze_document(doc_id):
    """
    Solicita análisis de documento al servicio de IA.
    Devuelve inmediatamente con un task_id para consultar el estado.
    El análisis real ocurre de forma asíncrona en el worker de IA.
    """
    user_id = get_jwt_identity()

    # Verificar que el documento existe y el usuario tiene permiso
    document = Document.query.get_or_404(doc_id)
    if not current_user_can_access(document, user_id):
        return jsonify({"error": "Acceso no autorizado"}), 403

    # Encolar la tarea en la cola específica de IA con prioridad normal
    task = analyze_document_task.apply_async(
        args=[doc_id, user_id],
        queue="ai",        # Worker específico de IA
        priority=5         # 0-9 en Redis: la prioridad depende del broker; verificar documentación
    )

    # Registrar en auditoría que se ha solicitado el análisis
    log_audit_event(
        user_id=user_id,
        action="DOCUMENT_ANALYSIS_REQUESTED",
        resource_id=doc_id,
        task_id=task.id
    )

    return jsonify({
        "task_id": task.id,
        "status": "processing",
        "message": "Análisis en curso. Consulte el estado con el task_id.",
        "status_url": f"/api/tasks/{task.id}/status"
    }), 202  # 202 Accepted — la petición fue recibida pero no procesada aún
