# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/agent_tools.py

from agents import function_tool
from sqlalchemy.orm import Session

@function_tool
async def evaluate_control_gap(
    framework_code: str,
    control_code: str | None = None,
    ens_category: str | None = None,
    context: dict = {}
) -> dict:
    """
    Evalúa el estado de cumplimiento de un control o marco completo.
    Para cada gap encontrado, sugiere acciones correctivas basadas
    en la guía del control y el contexto normativo.

    Args:
        framework_code: Código del marco (ENS, ISO27001, ISO27701)
        control_code: Código del control específico (opcional)
        ens_category: Categoría ENS si aplica (BASICA, MEDIA, ALTA)
    """
    db: Session = context.get("db")
    rag_service = context.get("rag_service")

    framework = db.query(ComplianceFramework).filter_by(
        code=framework_code
    ).first()

    if not framework:
        return {"error": f"Marco '{framework_code}' no encontrado"}

    if control_code:
        # Evaluación de control individual
        control = db.query(ComplianceControl).filter_by(
            framework_id=framework.id,
            code=control_code
        ).first()

        if not control:
            return {"error": f"Control '{control_code}' no encontrado"}

        # Buscar contexto normativo en RAG
        rag_context = ""
        if rag_service:
            rag_results = await rag_service.search(
                query=f"{framework_code} {control_code} {control.name}",
                collection="normativa_compliance",
                top_k=3
            )
            rag_context = "\n".join(
                r.content for r in rag_results
            )

        return {
            "control": {
                "code": control.code,
                "name": control.name,
                "description": control.description,
                "compliance_status": control.compliance_status.value,
                "implementation_status": control.implementation_status.value,
            },
            "evidences": [
                {
                    "title": e.title,
                    "type": e.evidence_type.value,
                    "collected_at": e.collected_at.isoformat(),
                    "is_expired": (
                        e.expires_at and e.expires_at < datetime.utcnow()
                    ) if e.expires_at else False
                }
                for e in control.evidences if e.is_valid
            ],
            "mapped_controls": [
                {
                    "framework": m.target_control.framework.code,
                    "code": m.target_control.code,
                    "name": m.target_control.name,
                    "status": m.target_control.compliance_status.value,
                    "mapping_type": m.mapping_type.value
                }
                for m in db.query(ControlMapping).filter(
                    ControlMapping.source_control_id == control.id
                ).all()
            ],
            "normative_context": rag_context
        }

    # Evaluación de marco completo: delegar a gap_analysis
    # (ver endpoint anterior)
    return await gap_analysis(
        framework.id, ens_category=ens_category, db=db
    )
