# Extraído de: LibroDevSecOps/cap-22-compliance-continuo.md
from fastapi import FastAPI
from typing import Optional

app = FastAPI(title="Compliance Dashboard API")


@app.get("/api/compliance/status")
async def get_compliance_status(
    framework: Optional[str] = None,
) -> dict:
    """Estado actual de compliance por framework."""
    assessments = load_latest_assessments(framework)

    summary = {}
    for fw in set(a.control.framework for a in assessments):
        fw_assessments = [
            a for a in assessments if a.control.framework == fw
        ]
        compliant = sum(
            1 for a in fw_assessments
            if a.status == ComplianceStatus.COMPLIANT
        )
        total = len(fw_assessments)
        summary[fw] = {
            "compliant": compliant,
            "total": total,
            "percentage": (
                round(compliant / total * 100, 1) if total > 0 else 0
            ),
            "last_assessed": max(
                a.assessed_at for a in fw_assessments
            ).isoformat(),
            "non_compliant_controls": [
                {
                    "id": a.control.control_id,
                    "title": a.control.title,
                    "cause": a.justification,
                }
                for a in fw_assessments
                if a.status == ComplianceStatus.NON_COMPLIANT
            ],
        }

    return {
        "frameworks": summary,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/compliance/drift")
async def get_compliance_drift(days: int = 30) -> dict:
    """Derivas de compliance en los últimos N días."""
    drifts = load_recent_drifts(days)
    return {
        "period_days": days,
        "total_drifts": len(drifts),
        "critical": [d for d in drifts if d["severity"] == "critical"],
        "high": [d for d in drifts if d["severity"] == "high"],
    }
