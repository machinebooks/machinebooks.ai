# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: destrucción robusta de VM
# Patrón: backend/services/proxmox_sdk_service.py (acción "destroy")

if action == "destroy":
    # 1. Verificar estado actual
    current = client.nodes(node).qemu(vmid).status.current.get()

    # 2. Si está bloqueada, esperar unos segundos
    if current.get("lock"):
        time.sleep(5)

    # 3. Si está corriendo, detenerla primero
    if current.get("status") == "running":
        client.nodes(node).qemu(vmid).status.stop.post()
        # Esperar hasta 15 segundos a que se detenga
        for _ in range(15):
            st = client.nodes(node).qemu(vmid).status.current.get()
            if st.get("status") == "stopped":
                break
            time.sleep(1)

    # 4. Intentar eliminar con purge (elimina discos)
    try:
        client.nodes(node).qemu(vmid).delete(purge=1)
    except Exception as e:
        if "running" in str(e).lower() or "locked" in str(e).lower():
            # Reintento: forzar stop y eliminar de nuevo
            client.nodes(node).qemu(vmid).status.stop.post()
            time.sleep(5)
            client.nodes(node).qemu(vmid).delete(purge=1)
        elif "does not exist" in str(e).lower():
            return {"success": True, "message": "VM ya eliminada"}
        else:
            raise

    # 5. Verificar que realmente desapareció
    for _ in range(30):
        try:
            client.nodes(node).qemu(vmid).status.current.get()
            time.sleep(1)  # Sigue existiendo, esperar
        except Exception:
            return {"success": True, "message": f"VM {vmid} eliminada"}

    return {"success": False, "error": "VM no se destruyó tras 30s"}
