# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/pfsense_service.py — Reglas de firewall

@classmethod
def _configure_pfsense(cls, client, workzone) -> list:
    """Configurar pfSense para una workzone."""
    rule_ids = []
    vlan_tag = workzone.vlan_id
    descr = f"WZ_{workzone.id}"

    # 1. Crear VLAN en interfaz LAN (em1)
    client.create_vlan("em1", vlan_tag, f"{descr}_VLAN")

    # 2. Bloquear todo el tráfico (deny por defecto)
    rule = client.create_firewall_rule(
        interface=f"vlan{vlan_tag}",
        action="block",
        source="any",
        destination="any",
        description=f"{descr}_BLOCK_INTER_WZ",
    )
    if rule.get("data", {}).get("id"):
        rule_ids.append(rule["data"]["id"])

    # 3. Permitir tráfico DENTRO de la subred de la workzone
    rule = client.create_firewall_rule(
        interface=f"vlan{vlan_tag}",
        action="pass",
        source=workzone.network_cidr,
        destination=workzone.network_cidr,
        description=f"{descr}_ALLOW_INTRA",
    )
    if rule.get("data", {}).get("id"):
        rule_ids.append(rule["data"]["id"])

    # 4. Si internet está habilitado, permitir salida
    if workzone.internet_enabled:
        rule = client.create_firewall_rule(
            interface=f"vlan{vlan_tag}",
            action="pass",
            source=workzone.network_cidr,
            destination="any",
            description=f"{descr}_INTERNET",
        )
        if rule.get("data", {}).get("id"):
            rule_ids.append(rule["data"]["id"])

    # 5. Configurar servidor DHCP en la VLAN
    client.configure_dhcp(
        interface=f"vlan{vlan_tag}",
        range_start=workzone.dhcp_start,
        range_end=workzone.dhcp_end,
        gateway=workzone.gateway_ip,
    )

    # 6. Aplicar todos los cambios de golpe
    client.apply_firewall()

    return rule_ids
