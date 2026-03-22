# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
async def create_review_tasks_from_impact(
    update_id: int,
    affected_controls: list[dict],
    compliance_service: ComplianceService,
) -> list[dict]:
    """Crea tareas de revisión en el módulo de compliance
    para cada control identificado como afectado.

    affected_controls: [
        {"framework": "NIS2", "control_id": "21.2",
         "impact": "high", "reason": "Nuevo plazo de notificación"}
    ]
    """
    tasks_created = []
    for ctrl in affected_controls:
        if ctrl["impact"] in ("high", "medium"):
            task = await compliance_service.create_review_task(
                framework_name=ctrl["framework"],
                control_id=ctrl["control_id"],
                reason=f"Actualización normativa #{update_id}: "
                       f"{ctrl.get('reason', 'Cambio detectado')}",
                priority="high" if ctrl["impact"] == "high" else "medium",
            )
            tasks_created.append(task)
    return tasks_created
