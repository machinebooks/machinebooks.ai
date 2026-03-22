# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/pfsense_service.py — Setup de red

@classmethod
def setup_workzone_network(cls, workzone, db) -> dict:
    """Setup completo de red para una workzone.
    1. Asignar VLAN
    2. Calcular direccionamiento
    3. Configurar pfSense (si está disponible)
    """
    # Paso 1: Asignar VLAN si no tiene una
    if not workzone.vlan_id:
        workzone.vlan_id = cls.allocate_vlan(db)

    # Paso 2: Calcular direccionamiento determinista
    net = cls.calculate_network(workzone.vlan_id)
    workzone.network_cidr = net["network_cidr"]
    workzone.gateway_ip = net["gateway_ip"]
    workzone.dhcp_start = net["dhcp_start"]
    workzone.dhcp_end = net["dhcp_end"]
    db.commit()  # Persistir antes de configurar pfSense

    # Paso 3: Configurar pfSense si está disponible
    client = cls.get_client(workzone)
    if client and client.test_connection():
        try:
            rule_ids = cls._configure_pfsense(client, workzone)
            workzone.pfsense_rule_ids = rule_ids
            db.commit()
        except Exception as e:
            logger.error(
                f"Error configurando pfSense para "
                f"workzone {workzone.id}: {e}"
            )
            # La workzone existe pero sin pfSense configurado
            # — se puede reintentar manualmente

    return net
