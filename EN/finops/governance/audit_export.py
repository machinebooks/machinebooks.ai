# Source: The FinOps Engineer and the Machine -- Chapter 21
# Pattern: Audit export service (PDF, CSV, JSON)

# services/audit_export.py
import csv
import io
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from models.llm_audit import LLMUsageLog
from fastapi.responses import StreamingResponse


class AuditExportService:
    """
    Exports LLM usage data for external audit.
    Metadata only: prompt content is never exported.
    """

    METADATA_FIELDS = [
        "id", "tenant_id", "user_id", "task_type", "model",
        "model_version", "provider", "input_tokens", "output_tokens",
        "total_cost_usd", "total_cost_eur", "prompt_hash",
        "response_hash", "quality_score", "accepted_by_user",
        "decision_relevant", "risk_category", "regulatory_context",
        "agent_id", "execution_approved_by", "created_at",
    ]

    def __init__(self, db: Session):
        self.db = db

    def export_csv(
        self,
        tenant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        risk_category: Optional[str] = None,
        decision_relevant_only: bool = False,
    ) -> StreamingResponse:
        """Generates CSV with filtered audit records."""
        query = self.db.query(LLMUsageLog)
        if tenant_id:
            query = query.filter(LLMUsageLog.tenant_id == tenant_id)
        if start_date:
            query = query.filter(LLMUsageLog.created_at >= start_date)
        if end_date:
            query = query.filter(LLMUsageLog.created_at <= end_date)
        if risk_category:
            query = query.filter(LLMUsageLog.risk_category == risk_category)
        if decision_relevant_only:
            query = query.filter(LLMUsageLog.decision_relevant == True)

        records = query.order_by(LLMUsageLog.created_at).all()

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.METADATA_FIELDS)
        writer.writeheader()
        for record in records:
            row = {f: getattr(record, f, None) for f in self.METADATA_FIELDS}
            if row.get("created_at"):
                row["created_at"] = row["created_at"].isoformat()
            writer.writerow(row)

        output.seek(0)
        filename = f"llm_audit_{tenant_id or 'all'}_{datetime.utcnow():%Y%m%d}.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
