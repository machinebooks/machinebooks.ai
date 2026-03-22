# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: gestión de snapshots
# Patrón: backend/services/proxmox_sdk_service.py

# Crear snapshot con nombre y descripción
if action == "snapshot.create":
    snapname = params["snapname"]      # e.g. "pre-exercise"
    description = params.get("description", "")
    client.nodes(node).qemu(vmid).snapshot.post(
        snapname=snapname,
        description=description
    )
    return {"success": True, "message": f"Snapshot '{snapname}' creado"}

# Restaurar snapshot (rollback)
if action == "snapshot.restore":
    snapname = params["snapname"]
    client.nodes(node).qemu(vmid).snapshot(snapname).rollback.post()
    return {"success": True, "message": f"Snapshot '{snapname}' restaurado"}

# Listar snapshots existentes
if action == "snapshots":
    snaps = client.nodes(node).qemu(vmid).snapshot.get()
    return {"success": True, "items": snaps}
