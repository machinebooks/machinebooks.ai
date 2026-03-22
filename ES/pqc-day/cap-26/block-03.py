# Extraído de: LibroPQC/cap-26-criptografo-futuro.md
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import CryptoPolicy, CryptoFinding
from app.services.policy_engine import evaluate_against_policy

crypto_agility_bp = Blueprint("crypto_agility", __name__)

@crypto_agility_bp.route("/api/v1/evaluate", methods=["POST"])
@jwt_required()
def evaluate_algorithm():
    """Evalúa un algoritmo contra la política vigente de la organización.

    Uso típico en CI/CD: antes de mergear un PR que introduce
    uso de criptografía, el pipeline consulta si el algoritmo
    es aceptable según la política PQC de la organización.

    Request:
        {"algorithm": "RSA-2048", "use_case": "jwt_signing", "context": "production"}

    Response:
        {
            "algorithm": "RSA-2048",
            "pqc_compliant": false,
            "recommendation": "ML-DSA-65",
            "hybrid_option": "RSA-2048 + ML-DSA-65",
            "deadline": "2030-12-31",
            "severity": "high",
            "regulatory_refs": ["CNSA-2.0", "NIST-IR-8547"]
        }
    """
    data = request.get_json()
    org_id = get_jwt_identity()["organization_id"]

    # Obtener política activa de la organización
    policy = CryptoPolicy.query.filter_by(
        organization_id=org_id,
        is_active=True
    ).order_by(CryptoPolicy.version.desc()).first()

    if not policy:
        return jsonify({"error": "No active crypto policy"}), 404

    result = evaluate_against_policy(
        algorithm=data["algorithm"],
        use_case=data.get("use_case", "general"),
        context=data.get("context", "production"),
        policy=policy
    )

    return jsonify(result), 200


@crypto_agility_bp.route("/api/v1/readiness/<int:project_id>", methods=["GET"])
@jwt_required()
def get_pqc_readiness(project_id: int):
    """Devuelve el estado de preparación PQC de un proyecto.

    Incluye: % de activos migrados, hallazgos pendientes por severidad,
    y tiempo estimado hasta el deadline regulatorio más cercano.
    """
    org_id = get_jwt_identity()["organization_id"]

    findings = CryptoFinding.query.filter_by(
        project_id=project_id,
        organization_id=org_id
    ).all()

    total = len(findings)
    pqc_compliant = sum(1 for f in findings if f.pqc_compliant)
    critical = sum(1 for f in findings if f.severity == "critical" and not f.pqc_compliant)
    high = sum(1 for f in findings if f.severity == "high" and not f.pqc_compliant)

    return jsonify({
        "project_id": project_id,
        "total_findings": total,
        "pqc_compliant": pqc_compliant,
        "readiness_percentage": round(pqc_compliant / total * 100, 1) if total else 0,
        "pending_critical": critical,
        "pending_high": high,
        "overall_status": "ready" if critical == 0 and high == 0 else "migration_needed"
    }), 200
