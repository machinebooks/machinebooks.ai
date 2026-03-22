# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_manager.py
# Operaciones de snapshot delegadas al SDK de bajo nivel

async def create_snapshot(
    self,
    cluster_id: int,
    vmid: int,
    snapshot_name: str,
    description: str = "",
    include_ram: bool = False
) -> bool:
    """
    Crear snapshot de VM.
    include_ram=True captura también el estado de la memoria (más lento).
    """
    vm = self.db.query(ProxmoxVM).filter(
        ProxmoxVM.cluster_id == cluster_id,
        ProxmoxVM.vmid == vmid
    ).first()

    if not vm:
        raise ValueError(f"VM {vmid} no encontrada en base de datos")

    node = self.db.query(ProxmoxNode).get(vm.node_id)
    sdk = self._get_live_sdk()
    return await sdk.create_snapshot(
        node.name, vmid, snapshot_name,
        description, include_ram
    )

async def restore_snapshot(
    self,
    cluster_id: int,
    vmid: int,
    snapshot_name: str
) -> bool:
    """
    Restaurar VM a un snapshot previo.
    La VM debe estar detenida para restaurar sin include_ram.
    """
    vm = self.db.query(ProxmoxVM).filter(
        ProxmoxVM.cluster_id == cluster_id,
        ProxmoxVM.vmid == vmid
    ).first()

    node = self.db.query(ProxmoxNode).get(vm.node_id)
    sdk = self._get_live_sdk()
    return await sdk.restore_snapshot(node.name, vmid, snapshot_name)
