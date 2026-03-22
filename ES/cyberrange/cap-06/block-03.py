# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Clonación de template con soporte para clones vinculados y completos

if action == "clone":
    template_vmid = int(params["template_vmid"])
    name = params["name"]
    linked = bool(params.get("linked", True))  # Vinculado por defecto
    node = params.get("node") or _resolve_node(type, template_vmid)
    tag = params.get("tag", "cyberrange")

    # Asignar VMID automáticamente si no se especifica
    new_vmid = params.get("new_vmid")
    if new_vmid is None:
        new_vmid = _get_next_vmid_from(min_vmid=200)

    if type == "qemu":
        payload = {
            "newid": new_vmid,
            "name": name,
            "full": 0 if linked else 1  # 0 = vinculado, 1 = completo
        }
        if description:
            payload["description"] = description
        if storage:
            payload["storage"] = storage

        # Ejecutar clonación
        result = client.nodes(node).qemu(template_vmid).clone.post(**payload)

        # Esperar a que se libere el bloqueo de la VM
        _await_unlock("qemu", node, new_vmid)

        # Etiquetar la VM para identificarla como parte del Cyber Range
        client.nodes(node).qemu(new_vmid).config.put(tags=tag)

        return {
            "success": True,
            "new_vmid": new_vmid,
            "node": node,
            "type": "qemu"
        }
