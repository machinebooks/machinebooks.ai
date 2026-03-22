# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: flujo completo de una operación

# 1. Router recibe la petición
@router.post("/{cluster_id}/vms/{vmid}/start")
async def start_vm(
    cluster_id: int,
    vmid: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("admin"))
):
    # 2. Delega al servicio
    result = manager.start_vm(db, cluster_id, vmid)

    # 3. Registra en auditoría
    audit_service.log(
        user_id=current_user.id,
        action="vm.start",
        resource=f"vm:{vmid}",
        severity="info"
    )

    return result
