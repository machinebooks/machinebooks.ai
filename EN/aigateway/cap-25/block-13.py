# Extracted from: LibroAIGateway/cap-25-mcp-registration-catalog.md
def _is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host:
        return False
    # Case 1: IP literal — direct validation
    try:
        ip = ipaddress.ip_address(host)
        return _is_safe_ip(ip)
    except ValueError:
        pass
    # Case 2: hostname — resolve DNS and validate all IPs
    resolved = socket.getaddrinfo(host, None, socket.AF_UNSPEC)
    for _family, _type, _proto, _canon, addr in resolved:
        ip = ipaddress.ip_address(addr[0])
        if not _is_safe_ip(ip):
            return False
    return True
