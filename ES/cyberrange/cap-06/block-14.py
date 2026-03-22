# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Detección de IP: diferente para KVM (Guest Agent) y LXC (interfaces)

def _fetch_ip(vm_type, vmid, node):
    """
    Obtener IP de una VM/contenedor.
    - QEMU: requiere QEMU Guest Agent instalado
    - LXC: consulta directa a interfaces del contenedor
    """
    if vm_type == "lxc":
        # LXC: acceso directo a interfaces de red
        interfaces = client.nodes(node).lxc(vmid).interfaces.get()
        for iface in interfaces:
            for addr in iface.get("ip-addresses", []):
                if addr.get("ip-address-type") == "ipv4":
                    ip = addr["ip-address"]
                    if _is_valid_private_ip(ip):
                        return ip
        return None

    # QEMU: requiere Guest Agent
    # Primero verificar que la VM está encendida
    status = client.nodes(node).qemu(vmid).status.current.get()
    if status.get("status") != "running":
        return None

    # Verificar que el Guest Agent responde
    try:
        client.nodes(node).qemu(vmid).agent.ping.post()
    except Exception:
        return None  # Guest Agent no instalado o no activo

    # Obtener interfaces de red vía Guest Agent
    data = client.nodes(node).qemu(vmid).agent(
        "network-get-interfaces"
    ).get()
    for iface in data.get("result", []):
        for addr in iface.get("ip-addresses", []):
            if addr.get("ip-address-type") == "ipv4":
                ip = addr["ip-address"]
                if _is_valid_private_ip(ip):
                    return ip
    return None
