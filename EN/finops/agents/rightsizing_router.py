# Source: The FinOps Engineer and the Machine -- Chapter 14
# Pattern: FastAPI routes for rightsizing

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
    scheduled_date: str | None = None  # ISO format if postponed


@router.get("/recommendations")
async def get_recommendations():
    """
    Returns rightsizing recommendations pending approval.
    Ordered by descending annual savings.
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
    Records the approval or rejection decision for a recommendation.
    If approved, schedules the change execution.
    """
    db = next(get_db())
    rec = db.query(RightsizingRecommendation).filter(
        RightsizingRecommendation.id == recommendation_id
    ).first()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = (
        ApprovalStatus.APPROVED if decision.approved
        else ApprovalStatus.REJECTED
    )
    rec.approved_by = decision.approver_id
    rec.approved_at = datetime.utcnow()
    rec.approval_notes = decision.notes

    if decision.approved:
        # Schedule execution for the indicated date or immediately
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
