# Source: The FinOps Engineer and the Machine -- Chapter 21
# Pattern: Audit API endpoints

# routers/audit.py
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from services.audit_export import AuditExportService
from auth import require_role

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


@router.get("/export/csv")
def export_audit_csv(
    tenant_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    risk_category: Optional[str] = Query(None),
    decision_relevant_only: bool = Query(False),
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin", "auditor", "compliance"])),
):
    """Exports LLM usage data in CSV for external audit."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    service = AuditExportService(db)
    return service.export_csv(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        risk_category=risk_category,
        decision_relevant_only=decision_relevant_only,
    )


@router.get("/compliance-summary")
def get_compliance_summary(
    tenant_id: Optional[int] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin", "auditor", "compliance", "finops"])),
):
    """Compliance summary: identifies anomalous usage patterns."""
    service = AuditExportService(db)
    return service.get_compliance_summary(tenant_id=tenant_id, days=days)
