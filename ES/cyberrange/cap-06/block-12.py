# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Listado de templates con metadatos de configuración

if action == "templates":
    templates = []
    for node in _nodes():
        for vm in client.nodes(node).qemu.get():
            if vm.get("template") == 1:  # Solo templates
                vmid = vm["vmid"]
                config = client.nodes(node).qemu(vmid).config.get()
                templates.append({
                    "vmid": vmid,
                    "name": vm.get("name", f"TEMPLATE-{vmid}"),
                    "description": config.get("description", ""),
                    "cores": config.get("cores", 1),
                    "memory": config.get("memory", 512),
                    "disk": _calc_disk_size_gb(config),
                    "node": node,
                    "type": "qemu"
                })
    return {"success": True, "items": templates}
