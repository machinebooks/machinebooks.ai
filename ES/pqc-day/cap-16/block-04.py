# Extraído de: LibroPQC/cap-16-dora.md
"""
Blueprint Flask para assessments DORA-PQC.
Expone endpoints para ejecutar, consultar y exportar
evaluaciones de preparación post-cuántica bajo DORA.
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

dora_bp = Blueprint("dora", __name__, url_prefix="/api/v1/dora")

@dora_bp.route("/assessment", methods=["POST"])
@jwt_required()
def run_assessment():
    """
    Ejecuta un assessment DORA-PQC completo.
    Requiere que la organización tenga hallazgos criptográficos previos.
    """
    user = get_jwt_identity()
    org_id = request.json.get("organization_id")

    # Verificar que el usuario pertenece a la organización (multi-tenant)
    if not user_belongs_to_org(user, org_id):
        return jsonify({"error": "Acceso denegado"}), 403

    # Obtener hallazgos criptográficos existentes
    findings = get_crypto_findings(org_id)
    if not findings:
        return jsonify({
            "error": "No hay hallazgos criptográficos. "
                     "Ejecute primero un análisis de código o certificados."
        }), 400

    # Configuración de pesos (por defecto o personalizados)
    weights = request.json.get("weights", DEFAULT_WEIGHTS)
    entity_profile = get_entity_profile(org_id)

    # Calcular scoring multidimensional
    score = calculate_overall_score(findings, weights=weights)

    # Evaluar controles DORA-PQC
    controls_status = evaluate_dora_controls(org_id, findings)

    # Generar explicación auditable con Claude
    explanation = generate_audit_explanation(
        score=score.__dict__,
        findings_summary=summarize_findings(findings),
        entity_profile=entity_profile,
    )

    # Persistir assessment
    assessment = save_assessment(
        org_id=org_id,
        score=score,
        controls=controls_status,
        explanation=explanation,
    )

    # Registrar en audit log (Art. 23 DORA: auditoría)
    log_audit_event(
        action="dora_assessment_completed",
        user=user,
        org_id=org_id,
        details={
            "assessment_id": assessment.id,
            "overall_score": score.overall_score,
            "risk_category": score.risk_category,
            "findings_count": len(findings),
        },
    )

    return jsonify({
        "assessment_id": assessment.id,
        "score": score.__dict__,
        "controls_evaluated": len(controls_status),
        "critical_gaps": len(score.critical_gaps) if hasattr(score, 'critical_gaps') else 0,
        "risk_category": score.risk_category,
        "g7_deadline_days": score.g7_deadline_days,
    }), 201


@dora_bp.route("/assessment/<int:assessment_id>/report", methods=["GET"])
@jwt_required()
def download_report(assessment_id):
    """
    Descarga el informe DORA-PQC en formato PDF.
    Incluye scoring, hallazgos, calendario regulatorio y recomendaciones.
    """
    user = get_jwt_identity()
    assessment = get_assessment(assessment_id)

    if not assessment or not user_belongs_to_org(user, assessment.org_id):
        return jsonify({"error": "Assessment no encontrado"}), 404

    # Generar PDF bajo demanda
    report_path = generate_dora_pdf(assessment)

    return send_file(
        report_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=(
            f"DORA-PQC-Assessment-{assessment.org_id}"
            f"-{datetime.now().strftime('%Y%m%d')}.pdf"
        ),
    )
