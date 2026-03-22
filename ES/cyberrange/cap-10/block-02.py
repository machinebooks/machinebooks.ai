# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: resolución automática de nodo y tipo
# Patrón: backend/services/proxmox_sdk_service.py (helpers internos)

def _resolve_node(vm_type: str, vmid: int) -> Optional[str]:
    """Encontrar en qué nodo del cluster está una VM."""
    for node in _nodes():
        try:
            for item in client.nodes(node).__getattr__(vm_type).get():
                if item.get("vmid") == vmid:
                    return node
        except Exception:
            continue
    return None

def _detect_type(vmid: int) -> Optional[str]:
    """Detectar si un vmid es QEMU o LXC probando ambos."""
    for node in _nodes():
        try:
            client.nodes(node).qemu(vmid).status.current.get()
            return "qemu"
        except Exception:
            pass
        try:
            client.nodes(node).lxc(vmid).status.current.get()
            return "lxc"
        except Exception:
            pass
    return None
