# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/pfsense_service.py — Limpieza de red

@classmethod
def cleanup_workzone_network(cls, workzone, db) -> None:
    """Eliminar todos los recursos de red de una workzone."""
    client = cls.get_client(workzone)

    if client and client.test_connection():
        # 1. Eliminar reglas de firewall registradas
        if workzone.pfsense_rule_ids:
            for rule_id in workzone.pfsense_rule_ids:
                try:
                    client.delete_firewall_rule(str(rule_id))
                except Exception as e:
                    logger.warning(
                        f"No se pudo eliminar regla {rule_id}: {e}"
                    )

        # 2. Eliminar VLAN
        if workzone.vlan_id:
            try:
                client.delete_vlan(str(workzone.vlan_id))
            except Exception as e:
                logger.warning(
                    f"No se pudo eliminar VLAN "
                    f"{workzone.vlan_id}: {e}"
                )

        # 3. Aplicar cambios
        try:
            client.apply_firewall()
        except Exception:
            pass

    # 4. Limpiar campos de red en base de datos
    workzone.vlan_id = None
    workzone.network_cidr = None
    workzone.gateway_ip = None
    workzone.dhcp_start = None
    workzone.dhcp_end = None
    workzone.pfsense_rule_ids = None
    db.commit()

    logger.info(
        f"Limpieza de red completada para workzone {workzone.id}"
    )
