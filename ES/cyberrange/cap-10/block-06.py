# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: obtención de ticket VNC
# Patrón: backend/services/proxmox_sdk_service.py (acción "vncproxy")

if action == "vncproxy":
    # Solicitar ticket VNC al nodo donde esta la VM
    websocket = params.get("websocket", 1)
    result = client.nodes(node).qemu(vmid).vncproxy.post(
        websocket=websocket
    )
    return {
        "success": True,
        "result": {
            "ticket": result.get("ticket"),   # Token temporal
            "port": result.get("port"),        # Puerto del websocket
            "cert": result.get("cert", ""),    # Certificado
            "vmid": vmid,
            "node": node,
            "type": type
        }
    }
