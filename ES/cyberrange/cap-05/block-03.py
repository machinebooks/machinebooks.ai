# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/services/proxmox_sync.py
# Patrón fuente de verdad: Proxmox manda, MySQL refleja

class ProxmoxSDKManager:
    """
    ARQUITECTURA DE SINCRONIZACIÓN:
    1. Proxmox = Fuente de verdad (operaciones van aquí)
    2. MySQL = Caché/mirror (NUNCA modifica infraestructura)
    3. Hooks = Únicos que escriben en MySQL tras operación Proxmox

    FLUJO DE LECTURA (web, rápido):
      Frontend → Backend → MySQL (instantáneo, sin tocar Proxmox)

    FLUJO DE ESCRITURA (operación):
      Frontend → Backend → Proxmox → Hook → MySQL

    FLUJO DE RECONCILIACIÓN (background):
      Proxmox → AutoSyncService → MySQL (cada 15 min)
    """

    def start_vm(self, db: Session, cluster_id: int, vmid: int) -> dict:
        """Arranca una VM: primero Proxmox, luego MySQL."""

        # 1. Enviar la orden a Proxmox (fuente de verdad)
        result = proxmox_sdk.proxmox(
            type="qemu",
            action="start",
            vmid=vmid
        )

        if not result["success"]:
            return {"error": f"Proxmox rechazó la operación: {result['error']}"}

        # 2. Solo si Proxmox confirma, actualizar MySQL
        vm = db.query(ProxmoxVM).filter_by(
            cluster_id=cluster_id,
            vmid=vmid
        ).first()

        if vm:
            vm.status = "running"
            vm.last_sync = datetime.now()
            db.commit()

        return {"success": True, "vmid": vmid, "status": "running"}

    def get_vms(self, db: Session, cluster_id: int) -> list:
        """Lee VMs: SIEMPRE de MySQL, NUNCA de Proxmox directamente."""
        # Las lecturas van a MySQL para no saturar la API de Proxmox
        # La sincronización periódica mantiene los datos actualizados
        return db.query(ProxmoxVM).filter_by(
            cluster_id=cluster_id
        ).all()
