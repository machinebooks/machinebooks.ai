# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: obtención de VMs desde MySQL (sin Proxmox)
# Patrón: backend/services/proxmox_sdk_manager.py

async def get_vms(self, cluster_id: int = None) -> Dict[str, Any]:
    """
    VMs SOLO desde MySQL. Instantáneo. Sin timeout.
    CRITICAL: Solo retorna VMs reales (no templates).
    """
    query = self.db.query(ProxmoxVM)
    if cluster_id:
        query = query.filter(ProxmoxVM.cluster_id == cluster_id)
    mysql_vms = query.all()

    vms_data = []
    for vm in mysql_vms:
        node = self.db.query(ProxmoxNode).filter(
            ProxmoxNode.id == vm.node_id
        ).first()

        vms_data.append({
            'vmid': vm.vmid,
            'name': vm.name,
            'status': vm.status,
            'node': node.name if node else 'unknown',
            'cpu_cores': vm.cpu_cores,
            'memory_mb': vm.memory_mb,
            'can_start': vm.status in ['stopped', 'paused'],
            'can_stop': vm.status == 'running',
            'sync_info': {
                'needs_sync': vm.last_sync is None or
                    (datetime.utcnow() - vm.last_sync).seconds > 300
            }
        })

    return {
        'vms': vms_data,
        'total_count': len(vms_data),
        'data_freshness': {
            'source': 'mysql_cached',
            'instant_response': True,
            'no_timeout_risk': True
        }
    }
