# Extraído de: LibroFinOps/cap-14-rightsizing-ia.md
# api/routes/rightsizing.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from models.rightsizing import RightsizingRecommendation, ApprovalStatus

router = APIRouter(prefix="/rightsizing", tags=["Rightsizing"])


class ApprovalDecision(BaseModel):
    recommendation_id: int
    approved: bool
    approver_id: str
    notes: str | None = None
    scheduled_date: str | None = None  # ISO format si se pospone


@router.get("/recommendations")
async def get_recommendations():
    """
    Devuelve las recomendaciones de rightsizing pendientes de aprobación.
    Ordenadas por ahorro anual descendente.
    """
    db = next(get_db())
    recs = db.query(RightsizingRecommendation).filter(
        RightsizingRecommendation.status == ApprovalStatus.PENDING
    ).order_by(
        RightsizingRecommendation.annual_savings_usd.desc()
    ).all()

    return {
        'recommendations': [r.to_dict() for r in recs],
        'total_potential_savings_usd': sum(r.annual_savings_usd for r in recs)
    }


@router.post("/approve/{recommendation_id}")
async def approve_recommendation(
    recommendation_id: int,
    decision: ApprovalDecision
):
    """
    Registra la decisión de aprobación o rechazo de una recomendación.
    Si se aprueba, programa la ejecución del cambio.
    """
    db = next(get_db())
    rec = db.query(RightsizingRecommendation).filter(
        RightsizingRecommendation.id == recommendation_id
    ).first()

    if not rec:
        raise HTTPException(status_code=404, detail="Recomendación no encontrada")

    rec.status = (
        ApprovalStatus.APPROVED if decision.approved
        else ApprovalStatus.REJECTED
    )
    rec.approved_by = decision.approver_id
    rec.approved_at = datetime.utcnow()
    rec.approval_notes = decision.notes

    if decision.approved:
        # Programamos la ejecución para la fecha indicada o inmediatamente
        scheduled_date = (
            datetime.fromisoformat(decision.scheduled_date)
            if decision.scheduled_date
            else datetime.utcnow()
        )
        execute_rightsizing.apply_async(
            args=[rec.instance_id, rec.recommended_type],
            eta=scheduled_date
        )
        rec.scheduled_execution = scheduled_date

    db.commit()
    return {'status': 'ok', 'decision': decision.approved}
