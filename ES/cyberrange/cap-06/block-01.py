# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Función unificada para todas las operaciones contra Proxmox VE

def proxmox(type: str, action: str, **params) -> Dict[str, Any]:
    """
    Punto de entrada único para operar con Proxmox VE.

    Args:
        type: 'qemu' | 'lxc' | 'auto' | 'all'
        action: operación a ejecutar (ver mapa de acciones)
        **params: argumentos específicos por acción

    Returns:
        dict con 'success' (bool) y 'result'/'items'/'error'

    Acciones soportadas:
        test, nodes, cluster.status, node.info,
        list, templates, status, config,
        start, stop, restart, destroy,
        snapshots, snapshot.create, snapshot.restore,
        clone, nextid, ip, firewall.enable,
        vncproxy, vncwebsocket, login
    """
    # Conexión cacheada: se reutiliza entre llamadas
    ok, client, err = _ensure_connection()
    if not ok:
        return {"success": False, "error": f"Sin conexión: {err}"}

    # Despacho por acción...
