# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/routes.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

router = APIRouter(prefix="/compliance", tags=["compliance"])

@router.get("/frameworks/{framework_id}/gap-analysis")
async def gap_analysis(
    framework_id: int,
    evidence_max_age_days: int = Query(
        default=365,
        description="Días máximos de antigüedad de evidencia"
    ),
    ens_category: str | None = Query(
        default=None,
        description="Categoría ENS: BASICA, MEDIA, ALTA"
    ),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Analiza gaps de cumplimiento para un framework.
    Devuelve controles sin evidencia, con evidencia caducada
    o en estado no evaluado.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=evidence_max_age_days)

    # Obtener todos los controles del framework (solo hojas, no categorías)
    controls = db.query(ComplianceControl).filter(
        ComplianceControl.framework_id == framework_id,
        ComplianceControl.level > 0  # Excluir categorías padre
    ).all()

    gaps = {
        "not_assessed": [],
        "no_evidence": [],
        "expired_evidence": [],
        "non_compliant": [],
        "partially_compliant": []
    }

    for control in controls:
        # Para ENS: filtrar por categoría si se especifica
        if ens_category and control.level_requirements:
            req = control.level_requirements.get(ens_category)
            if req == "no aplica":
                continue

        if control.compliance_status == ComplianceStatus.NOT_ASSESSED:
            gaps["not_assessed"].append(_control_summary(control))
            continue

        if control.compliance_status == ComplianceStatus.NON_COMPLIANT:
            gaps["non_compliant"].append(_control_summary(control))
            continue

        if control.compliance_status == ComplianceStatus.PARTIALLY_COMPLIANT:
            gaps["partially_compliant"].append(_control_summary(control))

        # Verificar evidencias
        valid_evidences = [
            e for e in control.evidences
            if e.is_valid and e.collected_at >= cutoff_date
        ]

        if not valid_evidences:
            category = (
                "expired_evidence" if control.evidences
                else "no_evidence"
            )
            gaps[category].append(_control_summary(control))

    # Resumen estadístico
    total_applicable = len([
        c for c in controls
        if c.compliance_status != ComplianceStatus.NOT_APPLICABLE
    ])
    total_gaps = sum(len(v) for v in gaps.values())

    return {
        "framework_id": framework_id,
        "analysis_date": datetime.utcnow().isoformat(),
        "total_controls": len(controls),
        "total_applicable": total_applicable,
        "total_gaps": total_gaps,
        "compliance_percentage": round(
            (1 - total_gaps / max(total_applicable, 1)) * 100, 1
        ),
        "gaps": gaps
    }


def _control_summary(control: ComplianceControl) -> dict:
    """Resumen compacto de un control para el informe de gaps."""
    return {
        "id": control.id,
        "code": control.code,
        "name": control.name,
        "compliance_status": control.compliance_status.value,
        "implementation_status": control.implementation_status.value,
        "evidence_count": len(control.evidences),
        "last_evidence_date": max(
            (e.collected_at for e in control.evidences),
            default=None
        )
    }
