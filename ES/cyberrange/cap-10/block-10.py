# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: sincronización bidireccional de VMs
# Patrón: backend/services/proxmox_sdk_manager.py

async def sync_vms(self, cluster_id: int) -> Dict[str, Any]:
    """
    Sync bidireccional: Proxmox es verdad, MySQL es espejo.
    Fases: actualizar existentes -> eliminar obsoletas ->
           añadir nuevas -> commit
    """
    # Cooldown: evitar sincronizaciones demasiado frecuentes
    if not self._can_sync('vms'):
        return {'success': False, 'error': 'Cooldown activo'}

    self._update_sync_timestamp('vms')

    # FASE 1: Obtener datos de ambos lados
    sdk = self._get_live_sdk()
    proxmox_vms = await sdk.get_vms_from_cluster(cluster.host)
    mysql_vms = self.db.query(ProxmoxVM).filter(
        ProxmoxVM.cluster_id == cluster_id
    ).all()

    # Mapas por vmid para comparación O(1)
    proxmox_map = {vm['vmid']: vm for vm in proxmox_vms}
    mysql_map = {vm.vmid: vm for vm in mysql_vms}

    updated = added = deleted = 0

    # FASE 2: Actualizar VMs que existen en ambos lados
    for vmid in set(proxmox_map) & set(mysql_map):
        pvm = proxmox_map[vmid]
        mvm = mysql_map[vmid]
        mvm.name = pvm.get('name', mvm.name)
        mvm.status = pvm.get('status', mvm.status)
        mvm.cpu_cores = pvm.get('cpu_cores', mvm.cpu_cores)
        mvm.memory_mb = pvm.get('memory_mb', mvm.memory_mb)
        mvm.last_sync = datetime.utcnow()
        updated += 1

    # FASE 3: Eliminar de MySQL VMs que ya no existen en Proxmox
    for vmid in set(mysql_map) - set(proxmox_map):
        self.db.delete(mysql_map[vmid])
        deleted += 1

    # FASE 4: Anadir a MySQL VMs nuevas de Proxmox
    for vmid in set(proxmox_map) - set(mysql_map):
        pvm = proxmox_map[vmid]
        self.db.add(ProxmoxVM(
            cluster_id=cluster_id,
            vmid=vmid,
            name=pvm.get('name', f'vm-{vmid}'),
            status=pvm.get('status', 'unknown'),
            cpu_cores=pvm.get('cpu_cores'),
            memory_mb=pvm.get('memory_mb'),
            last_sync=datetime.utcnow()
        ))
        added += 1

    self.db.commit()
    return {
        'success': True,
        'updated_count': updated,
        'added_count': added,
        'deleted_count': deleted,
        'sync_type': 'bidirectional'
    }
