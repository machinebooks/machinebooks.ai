# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
from datetime import datetime
from sqlalchemy.orm import Session


def check_exception_for_finding(
    db: Session,
    finding_id: str,
    finding_source: str
) -> dict:
    """Consulta si un hallazgo tiene una excepción vigente aprobada."""

    exception = (
        db.query(SecurityException)
        .filter(
            SecurityException.finding_id == finding_id,
            SecurityException.finding_source == finding_source,
            SecurityException.status == ExceptionStatus.APPROVED,
            SecurityException.expires_at > datetime.utcnow()
        )
        .first()
    )

    if exception:
        return {
            "has_exception": True,
            "exception_id": exception.id,
            "approved_by": exception.approved_by,
            "expires_at": exception.expires_at.isoformat(),
            "compensating_controls": exception.compensating_controls,
            "risk_score": exception.agent_risk_score
        }

    return {"has_exception": False}


def pipeline_security_gate(
    db: Session,
    findings: list[dict]
) -> dict:
    """Gate de seguridad que respeta excepciones vigentes."""

    blocking = []
    warnings = []
    excepted = []

    for finding in findings:
        exc = check_exception_for_finding(
            db, finding["id"], finding["source"]
        )

        if exc["has_exception"]:
            # Hallazgo con excepción vigente: registrar, no bloquear
            excepted.append({
                **finding,
                "exception_id": exc["exception_id"],
                "expires_at": exc["expires_at"]
            })
        elif finding["severity"] in ("critical", "high"):
            blocking.append(finding)
        elif finding["severity"] == "medium":
            warnings.append(finding)

    return {
        "gate_passed": len(blocking) == 0,
        "blocking_findings": blocking,
        "warnings": warnings,
        "excepted_findings": excepted,
        "summary": (
            f"{len(blocking)} bloqueantes, "
            f"{len(warnings)} advertencias, "
            f"{len(excepted)} con excepción vigente"
        )
    }
