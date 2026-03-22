# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
@router.post("/scripts/{script_name}/execute",
             dependencies=[Depends(role_required("admin", "organizer", "red"))])
async def execute_powershell_script(script_name: str,
                                     background_tasks: BackgroundTasks):
    scripts = await powershell_service.discover_powershell_scripts()
    if script_name not in scripts:
        raise HTTPException(404, "Script no encontrado")

    session_id = await ExecutionService.start_powershell_execution(
        script_name
    )

    return {
        "session_id": session_id,
        "websocket_url": f"/ws/powershell/{session_id}",
        "script_name": script_name
    }
