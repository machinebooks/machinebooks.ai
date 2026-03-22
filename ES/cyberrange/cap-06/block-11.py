# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Generación de ticket VNC y URL de WebSocket

if action == "vncproxy":
    websocket = params.get("websocket", 1)
    result = client.nodes(node).qemu(vmid).vncproxy.post(
        websocket=websocket
    )
    return {
        "success": True,
        "result": {
            "ticket": result.get("ticket"),
            "port": result.get("port"),
            "vmid": vmid,
            "node": node,
            "type": type
        }
    }

if action == "vncwebsocket":
    ticket = params["ticket"]
    port = params["port"]
    return {
        "success": True,
        "result": {
            "websocket_url": (
                f"wss://{host}:{proxmox_port}/api2/json/"
                f"nodes/{node}/qemu/{vmid}/vncwebsocket"
                f"?port={port}&vncticket={encoded_ticket}"
            ),
            "ticket": ticket,
            "port": port
        }
    }
