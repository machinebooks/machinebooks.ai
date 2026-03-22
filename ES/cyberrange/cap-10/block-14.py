# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: activación de firewall en VM
# Patrón: backend/services/proxmox_sdk_service.py (acción "firewall.enable")

if action == "firewall.enable":
    pfsense_ip = params.get("pfsense_ip")
    services = params.get("services", [])

    # 1. Activar firewall con política por defecto DROP
    client.nodes(node).qemu(vmid).firewall.options.put(
        enable=1,
        policy_out="DROP"
    )

    # 2. Permitir trafico desde el firewall de la workzone
    if pfsense_ip:
        client.nodes(node).qemu(vmid).firewall.rules.post(
            type="in", action="ACCEPT", source=pfsense_ip
        )

    # 3. Permitir servicios adicionales
    for svc in services:
        rule = {"type": "in", "action": "ACCEPT"}
        if svc.get("source"): rule["source"] = svc["source"]
        if svc.get("proto"):  rule["proto"] = svc["proto"]
        if svc.get("port"):   rule["dport"] = svc["port"]
        client.nodes(node).qemu(vmid).firewall.rules.post(**rule)

    return {"success": True, "message": f"Firewall habilitado en VM {vmid}"}
