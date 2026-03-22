# Extraído de: LibroFinOps/cap-21-aiact-auditoria.md
# routers/audit.py
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from services.audit_export import AuditExportService
from auth import require_role

router = APIRouter(prefix="/api/v1/audit", tags=["Auditoría"])


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
    """Exporta datos de uso LLM en CSV para auditoría externa."""
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
    """Resumen de compliance: identifica patrones de uso anómalo."""
    service = AuditExportService(db)
    return service.get_compliance_summary(tenant_id=tenant_id, days=days)
