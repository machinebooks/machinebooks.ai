# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: clonado con espera de desbloqueo
# Patrón: backend/services/proxmox_sdk_service.py (acción "clone")

def _await_unlock(vm_type, node, vmid, timeout=60, interval=2):
    """Esperar hasta que la VM salga del estado locked."""
    waited = 0
    while waited < timeout:
        try:
            status = client.nodes(node).__getattr__(vm_type)(vmid) \
                .status.current.get()
            if status and "lock" not in status:
                return True
        except Exception:
            pass
        time.sleep(interval)
        waited += interval
    return False

# Acción "clone" con espera de desbloqueo y tag automático
if action == "clone":
    template_vmid = int(params["template_vmid"])
    name = params["name"]
    node = params.get("node") or _resolve_node(type, template_vmid)
    new_vmid = params.get("new_vmid") or _get_next_vmid_from(200)

    # Clon linked (rápido, comparte base) o full (independiente)
    linked = bool(params.get("linked", True))
    payload = {
        "newid": new_vmid,
        "name": name,
        "full": 0 if linked else 1
    }
    if params.get("storage"):
        payload["storage"] = params["storage"]

    # Ejecutar clonado en Proxmox
    client.nodes(node).qemu(template_vmid).clone.post(**payload)

    # Esperar a que el clon se desbloquee (max 60s)
    _await_unlock("qemu", node, new_vmid)

    # Aplicar tag para identificar VMs del Cyber Range
    try:
        client.nodes(node).qemu(new_vmid).config.put(
            tags=params.get("tag", "cyberrange")
        )
    except Exception:
        pass  # El tag es cosmético, no bloquea la operación

    return {
        "success": True,
        "new_vmid": new_vmid,
        "node": node,
        "type": "qemu"
    }
