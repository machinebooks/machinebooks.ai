# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/pfsense_service.py — Estado de red

@classmethod
def get_network_status(cls, workzone) -> dict:
    """Obtener estado completo de red de una workzone."""
    status = {
        "vlan_id": workzone.vlan_id,
        "network_cidr": workzone.network_cidr,
        "gateway_ip": workzone.gateway_ip,
        "dhcp_range": (
            f"{workzone.dhcp_start} - {workzone.dhcp_end}"
            if workzone.dhcp_start else None
        ),
        "internet_enabled": workzone.internet_enabled,
        "pfsense_ip": workzone.pfsense_ip,
        "pfsense_connected": False,
        "firewall_rules_count": (
            len(workzone.pfsense_rule_ids)
            if workzone.pfsense_rule_ids else 0
        ),
    }

    # Verificar conectividad con pfSense
    client = cls.get_client(workzone)
    if client:
        status["pfsense_connected"] = client.test_connection()

    return status
