# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Espera activa hasta que la VM esté desbloqueada

def _await_unlock(vm_type: str, node: str, vmid: int,
                  timeout=60, interval=2) -> bool:
    """
    Espera hasta que la VM esté desbloqueada (sin lock).
    Proxmox bloquea las VMs durante clonación, snapshot, etc.
    """
    waited = 0
    while waited < timeout:
        try:
            status = client.nodes(node).qemu(vmid).status.current.get()
            if status and "lock" not in status:
                return True  # VM desbloqueada
        except Exception:
            pass
        time.sleep(interval)
        waited += interval
    return False  # Timeout alcanzado
