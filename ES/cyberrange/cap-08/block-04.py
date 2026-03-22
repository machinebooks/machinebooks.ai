# Extraído de: LibroCyberrange/cap-08-workzones.md
# Ejemplo didáctico: routers/workzones.py — Asignar usuario

@router.post("/assign-user", response_model=UserAssignResponse)
async def assign_user_to_workzone(
    request: UserAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("admin"))
):
    """Asignar un usuario a una workzone — solo administradores."""
    workzone = db.query(Workzone).filter(
        Workzone.id == request.workzone_id
    ).first()
    if not workzone:
        raise HTTPException(404, "Workzone no encontrada")

    # Verificar que la workzone tiene app_id
    if not workzone.app_id:
        raise HTTPException(
            400,
            "La workzone debe tener un app_id para asignar usuarios"
        )

    # Verificar que el usuario no está en otra workzone
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    if user.workzone_id and user.workzone_id != request.workzone_id:
        raise HTTPException(
            400,
            f"El usuario ya está asignado a otra workzone"
        )

    # Asignar
    user.workzone_id = request.workzone_id
    db.commit()

    return UserAssignResponse(
        success=True,
        message="Usuario asignado correctamente",
        user_id=user.id,
        workzone_id=workzone.id,
    )
