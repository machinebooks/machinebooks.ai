# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/pfsense_service.py — Toggle de internet

@classmethod
def toggle_internet(cls, workzone, enable: bool, db) -> bool:
    """Activar/desactivar acceso a internet para una workzone."""
    client = cls.get_client(workzone)
    workzone.internet_enabled = enable

    if client and client.test_connection() and workzone.vlan_id:
        descr = f"WZ_{workzone.id}"

        if enable:
            # Crear regla de paso a internet + NAT de salida
            rule = client.create_firewall_rule(
                interface=f"vlan{workzone.vlan_id}",
                action="pass",
                source=workzone.network_cidr,
                destination="any",
                description=f"{descr}_INTERNET",
            )
            rule_ids = workzone.pfsense_rule_ids or []
            if rule.get("data", {}).get("id"):
                rule_ids.append(rule["data"]["id"])
            workzone.pfsense_rule_ids = rule_ids

            # Habilitar NAT de salida para la subred
            client.enable_outbound_nat(
                interface=f"vlan{workzone.vlan_id}",
                source_network=workzone.network_cidr,
            )
        else:
            # Buscar y eliminar regla de internet por descripción
            rules = client.get_firewall_rules()
            for r in rules:
                if r.get("descr") == f"{descr}_INTERNET":
                    client.delete_firewall_rule(str(r["id"]))

        client.apply_firewall()

    db.commit()
    return enable
