# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: operaciones de red
# Patrón: backend/services/proxmox_sdk_service.py

# Listar redes virtuales del cluster
if action == "vnetworks":
    vnets = client.cluster.sdn.vnets.get()
    return {"success": True, "items": vnets}

# Conectar VM a una red virtual
if action == "connect_network":
    vmid = int(params["vmid"])
    node = params["node"]
    network_name = params["network_name"]

    if type == "lxc":
        # LXC: configurar interfaz con DHCP
        client.nodes(node).lxc(vmid).config.put(
            net0=f"name=eth0,bridge={network_name},ip=dhcp"
        )
    else:
        # QEMU: configurar interfaz virtio
        client.nodes(node).qemu(vmid).config.post(
            net0=f"virtio,bridge={network_name}"
        )
    return {"success": True, "message": f"VM {vmid} conectada a {network_name}"}
