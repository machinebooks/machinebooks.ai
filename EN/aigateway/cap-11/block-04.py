# Extracted from: LibroAIGateway/cap-11-tools-code-web-documents.md
def _is_private_host(host: str) -> bool:
    """Rejects if any resolved IP falls into private/loopback networks."""
    # Strips brackets from literal IPv6
    h = host.strip().strip("[]")
    try:
        ip = ipaddress.ip_address(h)
        if _ip_is_unsafe(ip):
            return True
        # IPv6 mapped to IPv4 (::ffff:7f00:1 → 127.0.0.1)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            return _ip_is_unsafe(ip.ipv4_mapped)
        return False
    except ValueError:
        pass
    # DNS resolution: validates all resolved IPs
    for info in socket.getaddrinfo(h, None):
        ip = ipaddress.ip_address(info[4][0])
        if _ip_is_unsafe(ip):
            return True
    return False
