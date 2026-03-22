# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/pfsense_service.py — Asignación de VLANs

class NetworkIsolationService:
    """Gestión de alto nivel del aislamiento de red por workzone."""

    @staticmethod
    def allocate_vlan(db, vlan_start: int = 100,
                      vlan_end: int = 999) -> int:
        """Encontrar la siguiente VLAN disponible en el rango."""
        used_vlans = {
            wz.vlan_id for wz in
            db.query(Workzone).filter(
                Workzone.vlan_id.isnot(None)
            ).all()
        }
        for vlan_id in range(vlan_start, vlan_end + 1):
            if vlan_id not in used_vlans:
                return vlan_id
        raise ValueError(
            f"No hay VLANs disponibles en rango {vlan_start}-{vlan_end}"
        )

    @staticmethod
    def calculate_network(vlan_id: int) -> dict:
        """Calcular direccionamiento basado en VLAN ID.
        VLAN 100 -> 10.100.0.0/24
        VLAN 101 -> 10.101.0.0/24
        Para VLAN > 255: VLAN 300 -> 10.1.44.0/24
        """
        if vlan_id > 255:
            second_octet = vlan_id // 256
            third_octet = vlan_id % 256
        else:
            second_octet = vlan_id
            third_octet = 0

        return {
            "network_cidr": f"10.{second_octet}.{third_octet}.0/24",
            "gateway_ip":   f"10.{second_octet}.{third_octet}.1",
            "dhcp_start":   f"10.{second_octet}.{third_octet}.100",
            "dhcp_end":     f"10.{second_octet}.{third_octet}.200",
        }
