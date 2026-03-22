# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_manager.py
# Arquitectura del Manager: responsabilidades claras

class ProxmoxSDKManager:
    """
    ARQUITECTURA CORRECTA:
    1. PROXMOX = Fuente de VERDAD (todas las operaciones van aquí)
    2. MySQL = SOLO MIRROR/CACHE (NUNCA crea/elimina registros directamente)
    3. Hooks = ÚNICOS que escriben en MySQL (Proxmox -> Hooks -> MySQL)

    FLUJO CORRECTO WEB:
    - Mostrar datos: MySQL (instantáneo, sin timeout)
    - Sincronizar: Proceso separado en background
    - Operaciones VM: Proxmox -> Hook actualiza MySQL

    MÉTODOS QUE NUNCA CONECTAN A PROXMOX (para la web):
    - get_clusters()    = SOLO MySQL (rápido)
    - get_vms()         = SOLO MySQL (rápido)
    - get_templates()   = SOLO MySQL (rápido)

    MÉTODOS QUE SÍ CONECTAN A PROXMOX (operaciones):
    - start_vm(), stop_vm(), restart_vm()
    - create_vm_from_template()
    - delete_vm()
    """
