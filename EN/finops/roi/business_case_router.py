# Source: The FinOps Engineer and the Machine -- Chapter 18
# Pattern: FastAPI routes for business case generation

# routers/business_case.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services.business_case_generator import BusinessCaseGenerator
from auth import require_role

router = APIRouter(prefix="/api/v1/business-case", tags=["Business Case"])

@router.get("/executive-summary")
def get_executive_summary(
    tenant_id: int = Query(None),
    engineering_investment_eur: float = Query(47500.0),
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin", "cfo", "finops", "manager"])),
):
    """
    Generates the executive summary for CFO presentation.
    Includes real ROI, 12-month TCO, and three scenarios.
    """
    generator = BusinessCaseGenerator(db)
    summary = generator.generate(
        tenant_id=tenant_id,
        engineering_investment_eur=engineering_investment_eur,
        days_of_data=days,
    )
    return {
        "snapshot": {
            "generated_at": summary.generated_at.isoformat(),
            "monthly_llm_cost_eur": summary.monthly_llm_cost_eur,
            "monthly_value_eur": summary.monthly_value_liberated_eur,
            "roi_adjusted": f"{summary.roi_adjusted}:1",
            "break_even_month": summary.break_even_month,
            "year1_net_value_eur": summary.year1_net_value_eur,
        },
        "scenarios": summary.scenarios,
        "limitations": summary.limitations,
        "assumptions": summary.assumptions,
    }
