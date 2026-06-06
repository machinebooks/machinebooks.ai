# Extraído de: LibroAIGateway/cap-11-tools-codigo-web-documentos.md
def _ip_is_unsafe(ip) -> bool:
    return (
        ip.is_private      # 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
        or ip.is_loopback   # 127.0.0.0/8, ::1
        or ip.is_link_local # 169.254.0.0/16 (IMDS de cloud)
        or ip.is_multicast  # 224.0.0.0/4
        or ip.is_reserved
        or ip.is_unspecified  # 0.0.0.0, ::
    )
