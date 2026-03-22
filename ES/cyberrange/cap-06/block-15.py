# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Operaciones SDN: listar y conectar redes virtuales

if action == "vnetworks":
    vnets = client.cluster.sdn.vnets.get()
    return {"success": True, "items": vnets}

if action == "connect_network":
    vmid = int(params["vmid"])
    node = params["node"]
    network_name = params["network_name"]

    if type == "lxc":
        # LXC: configurar interfaz con IP por DHCP
        client.nodes(node).lxc(vmid).config.put(
            net0=f"name=eth0,bridge={network_name},ip=dhcp"
        )
    else:
        # QEMU: añadir interfaz virtio conectada al bridge
        client.nodes(node).qemu(vmid).config.post(
            net0=f"virtio,bridge={network_name}"
        )
    return {"success": True, "message": f"Conectado a {network_name}"}
