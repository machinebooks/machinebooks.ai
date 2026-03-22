# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: rutas/ai_governance.py
# Endpoint de evaluación de conformidad con scoring ponderado

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/api/v1/ai-governance", tags=["AI Governance"])


@router.get("/records/{record_id}/conformity-score")
async def get_conformity_score(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calcula el scoring de conformidad de un sistema de IA.

    Retorna puntuación 0-100 basada en los 7 checkpoints ponderados,
    con detalle por checkpoint y recomendaciones.
    """
    record = db.query(AIGovernanceRecord).filter_by(
        id=record_id,
        tenant_id=current_user.tenant_id,
        is_deleted=False
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Registro de IA no encontrado")

    if record.risk_level != AIRiskLevel.HIGH:
        return {
            "record_id": record_id,
            "risk_level": record.risk_level.value,
            "message": "La evaluación de conformidad completa solo aplica a sistemas de alto riesgo.",
            "applicable": False
        }

    # Obtener todas las evaluaciones del registro
    assessments = db.query(ConformityAssessment).filter_by(
        ai_record_id=record_id,
        is_deleted=False
    ).all()

    # Construir mapa de checkpoint → evaluación más reciente
    checkpoint_map = {}
    for assessment in assessments:
        existing = checkpoint_map.get(assessment.checkpoint)
        if not existing or (assessment.evaluation_date and
            (not existing.evaluation_date or
             assessment.evaluation_date > existing.evaluation_date)):
            checkpoint_map[assessment.checkpoint] = assessment

    # Calcular scoring ponderado
    total_score = 0.0
    checkpoint_details = []
    blocking_issues = []

    for checkpoint in ConformityCheckpoint:
        weight = CHECKPOINT_WEIGHTS[checkpoint]
        assessment = checkpoint_map.get(checkpoint)

        if not assessment or assessment.status == CheckpointStatus.NOT_STARTED:
            score = 0.0
            status = "not_started"
        elif assessment.status == CheckpointStatus.PASSED:
            score = 1.0
            status = "passed"
        elif assessment.status == CheckpointStatus.CONDITIONAL:
            score = 0.7  # Cumple con condiciones: 70% del peso
            status = "conditional"
        elif assessment.status == CheckpointStatus.IN_PROGRESS:
            score = 0.3  # En evaluación: reconoce el esfuerzo
            status = "in_progress"
        elif assessment.status == CheckpointStatus.FAILED:
            score = 0.0
            status = "failed"
            blocking_issues.append({
                "checkpoint": checkpoint.value,
                "article": _get_article_reference(checkpoint),
                "findings": assessment.findings
            })

        weighted_score = score * weight
        total_score += weighted_score

        checkpoint_details.append({
            "checkpoint": checkpoint.value,
            "article": _get_article_reference(checkpoint),
            "status": status,
            "weight": weight,
            "score": round(score * 100),
            "weighted_score": round(weighted_score * 100, 1),
            "evaluation_date": assessment.evaluation_date.isoformat() if assessment and assessment.evaluation_date else None,
            "evaluator_id": assessment.evaluator_id if assessment else None,
            "iso42001_controls": assessment.iso42001_controls if assessment else None
        })

    conformity_score = round(total_score * 100, 1)

    # Determinar estado global
    if blocking_issues:
        overall_status = "non_compliant"
    elif conformity_score >= 90:
        overall_status = "compliant"
    elif conformity_score >= 70:
        overall_status = "partially_compliant"
    else:
        overall_status = "non_compliant"

    return {
        "record_id": record_id,
        "system_name": record.name,
        "risk_level": record.risk_level.value,
        "conformity_score": conformity_score,
        "overall_status": overall_status,
        "checkpoints": checkpoint_details,
        "blocking_issues": blocking_issues,
        "recommendations": _generate_recommendations(checkpoint_details, blocking_issues),
        "last_full_assessment": max(
            (a.evaluation_date for a in assessments if a.evaluation_date),
            default=None
        )
    }


def _get_article_reference(checkpoint: ConformityCheckpoint) -> str:
    """Mapea cada checkpoint a su artículo del AI Act."""
    mapping = {
        ConformityCheckpoint.RISK_MANAGEMENT: "Art. 9",
        ConformityCheckpoint.DATA_GOVERNANCE: "Art. 10",
        ConformityCheckpoint.TECHNICAL_DOCS: "Art. 11",
        ConformityCheckpoint.RECORD_KEEPING: "Art. 12",
        ConformityCheckpoint.TRANSPARENCY: "Art. 13",
        ConformityCheckpoint.HUMAN_OVERSIGHT: "Art. 14",
        ConformityCheckpoint.ACCURACY_ROBUSTNESS: "Art. 15",
    }
    return mapping.get(checkpoint, "N/A")


def _generate_recommendations(details: list, blocking: list) -> list[str]:
    """Genera recomendaciones priorizadas según estado de checkpoints.

    Orden de prioridad: (1) checkpoints fallidos (bloqueantes),
    (2) checkpoints no iniciados (gap crítico),
    (3) checkpoints condicionales (mejora posible).
    """
    recommendations = []
    for issue in blocking:
        recommendations.append(
            f"BLOQUEANTE: {issue['checkpoint']} ({issue['article']}) — "
            f"requiere corrección antes de despliegue."
        )
    for d in details:
        if d["status"] == "not_started":
            recommendations.append(
                f"Iniciar evaluación de {d['checkpoint']} ({d['article']})."
            )
        elif d["status"] == "conditional":
            recommendations.append(
                f"Revisar condiciones de {d['checkpoint']} ({d['article']})."
            )
    return recommendations
