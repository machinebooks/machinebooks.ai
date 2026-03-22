# Extraído de: LibroCyberrange/cap-08-workzones.md
# Ejemplo didáctico: routers/workzones.py — Creación de workzone

class WorkzoneCreate(BaseModel):
    name: str
    app_id: Optional[int] = None
    cpu_limit: int = 32          # 32 cores por defecto
    memory_limit: int = 32768    # 32 GB por defecto
    storage_limit: int = 500     # 500 GB por defecto
    zone_ttl_hours: int = 4      # 4 horas por defecto
    current_zone: str = 'none'   # Modo de operación
    scenario_id: Optional[int] = None

@router.post("/", response_model=WorkzoneResponse)
async def create_workzone(
    workzone_data: WorkzoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("admin"))
):
    """Crear un nuevo workzone — solo administradores."""
    # Validar rango del app_id
    if workzone_data.app_id:
        if not (1 <= workzone_data.app_id <= 15):
            raise HTTPException(
                status_code=400,
                detail="El ID de aplicación debe estar entre 1 y 15"
            )
        # Verificar unicidad
        existing = db.query(Workzone).filter(
            Workzone.app_id == workzone_data.app_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"El app_id {workzone_data.app_id} ya está en uso"
            )

    workzone = Workzone(
        name=workzone_data.name,
        app_id=workzone_data.app_id,
        owner_user=current_user.id,
        cpu_limit=workzone_data.cpu_limit,
        memory_limit=workzone_data.memory_limit,
        storage_limit=workzone_data.storage_limit,
        zone_ttl_hours=workzone_data.zone_ttl_hours,
        current_zone=workzone_data.current_zone,
        scenario_id=workzone_data.scenario_id,
    )
    db.add(workzone)
    db.commit()
    db.refresh(workzone)
    return workzone
