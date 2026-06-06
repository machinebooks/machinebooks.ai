# Extraído de: LibroAIGateway/cap-11-tools-codigo-web-documentos.md
def _is_private_host(host: str) -> bool:
    """Rechaza si cualquier IP resuelta cae en redes privadas/loopback."""
    # Limpia brackets de IPv6 literales
    h = host.strip().strip("[]")
    try:
        ip = ipaddress.ip_address(h)
        if _ip_is_unsafe(ip):
            return True
        # IPv6 mapeado a IPv4 (::ffff:7f00:1 → 127.0.0.1)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            return _ip_is_unsafe(ip.ipv4_mapped)
        return False
    except ValueError:
        pass
    # DNS resolution: valida todas las IPs resueltas
    for info in socket.getaddrinfo(h, None):
        ip = ipaddress.ip_address(info[4][0])
        if _ip_is_unsafe(ip):
            return True
    return False
