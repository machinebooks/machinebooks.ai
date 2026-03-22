# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/services/proxmox_sdk_service.py
# Servicio unificado de comunicación con Proxmox VE

from proxmoxer import ProxmoxAPI

def proxmox(type: str, action: str, **params) -> dict:
    """
    Punto de entrada único para toda operación Proxmox.

    Tipos: 'qemu' | 'lxc' | 'auto' | 'all'
    Acciones: 'list', 'status', 'start', 'stop', 'clone',
              'destroy', 'snapshots', 'vncproxy', etc.

    Retorna siempre: {"success": bool, "result"/"error": ...}
    """

    # Conexión cacheada con reconexión automática
    client = _ensure_connection()

    if action == "list":
        # Listar VMs del tipo solicitado
        vms = []
        for node in client.nodes.get():
            if type in ("qemu", "all"):
                vms += client.nodes(node["node"]).qemu.get()
            if type in ("lxc", "all"):
                vms += client.nodes(node["node"]).lxc.get()
        return {"success": True, "items": vms}

    elif action == "start":
        vmid = params["vmid"]
        node = _find_node_for_vm(client, vmid)
        if type == "qemu":
            client.nodes(node).qemu(vmid).status.start.post()
        elif type == "lxc":
            client.nodes(node).lxc(vmid).status.start.post()
        return {"success": True, "message": f"VM {vmid} starting"}

    elif action == "clone":
        # Clonar desde template (linked clone para velocidad)
        source_vmid = params["template_vmid"]
        new_vmid = params.get("new_vmid") or _next_id(client)
        node = _find_node_for_vm(client, source_vmid)
        client.nodes(node).qemu(source_vmid).clone.post(
            newid=new_vmid,
            name=params.get("name", f"clone-{new_vmid}"),
            full=0,  # Linked clone: rápido, comparte disco base
            pool=params.get("pool"),
        )
        return {"success": True, "result": {"vmid": new_vmid}}

    elif action == "vncproxy":
        # Ticket VNC para consola en navegador
        vmid = params["vmid"]
        node = _find_node_for_vm(client, vmid)
        ticket = client.nodes(node).qemu(vmid).vncproxy.post()
        return {"success": True, "result": ticket}

    # ... más acciones: destroy, snapshots, firewall, etc.
