# Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
# routers/roi.py — Endpoints FastAPI para ROI
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services.roi_tracker import ROITracker
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/v1/roi", tags=["ROI"])

@router.get("/summary")
def get_roi_summary(
    days: int = Query(30, ge=1, le=365),
    tenant_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "finops", "manager"])),
):
    """Resumen de ROI con desglose por tipo de tarea."""
    tracker = ROITracker(db)
    return tracker.get_summary(tenant_id=tenant_id, days=days)

@router.post("/record")
def record_task_completion(
    task_type: str, llm_cost_eur: float,
    accepted: bool = True, role: str = "senior_consultant",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Registra manualmente la compleción de una tarea."""
    tracker = ROITracker(db)
    result = tracker.record_completion(
        task_type=task_type, llm_cost_eur=llm_cost_eur,
        accepted=accepted, role=role,
        user_id=current_user.id, tenant_id=current_user.tenant_id,
    )
    if result is None:
        return {"error": "Sin configuración de referencia para esta tarea"}
    return {
        "roi_gross": result.roi_gross, "roi_adjusted": result.roi_adjusted,
        "human_value_eur": result.human_value_eur, "llm_cost_eur": result.llm_cost_eur,
    }
