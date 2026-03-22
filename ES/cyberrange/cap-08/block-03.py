# Extraído de: LibroCyberrange/cap-08-workzones.md
# Ejemplo didáctico: routers/workzones.py — Descubrimiento de VMs

async def get_workzone_deployed_machines(
    db: Session, workzone: Workzone, current_user: User
) -> List[ProxmoxVM]:
    """Obtener VMs desplegadas en una workzone por tags y nombre."""

    # Método 1: Búsqueda directa por workzone_id en base de datos
    traditional = db.query(ProxmoxVM).filter(
        ProxmoxVM.workzone_id == workzone.id
    ).all()

    if not workzone.app_id and not workzone.scenario_id:
        return traditional

    # Método 2: Búsqueda avanzada por tags de Proxmox
    all_vms = db.query(ProxmoxVM).all()
    results = []

    if workzone.app_id:
        workzone_tag = f"wz{workzone.app_id:02d}"
        for vm in all_vms:
            vm_tags = (
                vm.tags.split(';')
                if isinstance(vm.tags, str) else
                vm.tags if isinstance(vm.tags, list) else []
            )
            if workzone_tag in vm_tags:
                results.append(vm)

    # Método 3: Búsqueda por prefijo de nombre de escenario
    if workzone.scenario_id:
        prefix = f"SCENE{workzone.scenario_id:05d}-"
        results.extend(
            vm for vm in all_vms if vm.name.startswith(prefix)
        )

    # Deduplicar resultados
    seen = set()
    unique = []
    for vm in results:
        if vm.id not in seen:
            unique.append(vm)
            seen.add(vm.id)

    return unique if unique else traditional
