# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Destrucción defensiva con apagado previo y reintentos

if action == "destroy":
    purge = int(params.get("purge", 1))  # Eliminar discos asociados

    # Verificar estado actual
    current = client.nodes(node).qemu(vmid).status.current.get()

    # Si está bloqueada, esperar
    if current.get("lock"):
        time.sleep(5)

    # Si está encendida, apagar primero
    if current.get("status") == "running":
        client.nodes(node).qemu(vmid).status.stop.post()
        # Esperar apagado con timeout
        for _ in range(15):
            status = client.nodes(node).qemu(vmid).status.current.get()
            if status.get("status") == "stopped":
                break
            time.sleep(1)

    # Intentar destrucción
    try:
        client.nodes(node).qemu(vmid).delete(purge=purge)
    except Exception as e:
        if "running" in str(e).lower() or "locked" in str(e).lower():
            # Reintento: apagar forzosamente y volver a intentar
            client.nodes(node).qemu(vmid).status.stop.post()
            time.sleep(5)
            client.nodes(node).qemu(vmid).delete(purge=purge)
        elif "does not exist" in str(e).lower():
            return {"success": True, "message": "Ya eliminada"}
