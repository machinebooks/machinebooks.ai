# Extraído de: LibroCyberrange/cap-13-escenarios-topologias.md
# backend/routers/scenarios.py — Endpoint de despliegue
@router.post("/templates/{template_id}/deploy")
async def deploy_scenario(
    template_id: int,
    deploy_request: ScenarioDeployRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lanza el despliegue asíncrono de un escenario."""
    template = db.query(ScenarioTemplate).get(template_id)
    if not template:
        raise HTTPException(404, "Template no encontrado")

    workzone = db.query(Workzone).get(deploy_request.workzone_id)
    if not workzone:
        raise HTTPException(404, "Workzone no encontrada")

    # Crear registro de despliegue
    deployment = ScenarioDeployment(
        scenario_template_id=template.id,
        user_id=current_user.id,
        workzone_id=workzone.id,
        status="deploying",
        progress=0,
        deployed_config=template.topology_config,
        deploy_started_at=datetime.utcnow()
    )
    db.add(deployment)
    db.commit()
    db.refresh(deployment)

    # Lanzar despliegue en background
    background_tasks.add_task(
        scenario_deployment_service.deploy_scenario,
        deployment_id=deployment.id,
        template=template,
        workzone=workzone,
        custom_config=deploy_request.custom_config,
        db=db
    )

    return {
        "deployment_id": deployment.id,
        "status": "deploying",
        "message": "Despliegue iniciado. Sigue el progreso vía WebSocket."
    }
