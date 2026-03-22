# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/backend/challenge_cleanup.py

CHECK_INTERVAL_SECONDS = 600          # 10 minutos entre comprobaciones
ORPHAN_CHECK_EVERY_N_CYCLES = 6       # Cada 60 minutos, buscar huérfanas

class ChallengeCleanupService:
    """Background thread: destruye instancias expiradas y huérfanas."""

    def _cleanup_expired(self):
        """Destruye VMs/CTs cuyo expires_at < now."""
        db = SessionLocal()
        try:
            expired = db.query(ChallengeInstance).filter(
                ChallengeInstance.expires_at != None,
                ChallengeInstance.expires_at < datetime.utcnow(),
                ChallengeInstance.vm_status.in_(['running', 'starting', 'cloning']),
                ChallengeInstance.vmid != None
            ).all()

            for instance in expired:
                result = proxmox(instance.vm_type or 'lxc', "destroy", vmid=instance.vmid)
                if result.get("success"):
                    instance.vm_status = 'destroyed'
                else:
                    instance.vm_status = 'error'

            db.commit()
        finally:
            db.close()

    def _cleanup_orphans(self):
        """Busca VMs con prefijo 'cr-' sin instancia asociada y las destruye."""
        db = SessionLocal()
        try:
            # VMIDs que tienen instancia activa en la BD
            active_vmids = {
                inst.vmid for inst in db.query(ChallengeInstance).filter(
                    ChallengeInstance.vmid != None,
                    ChallengeInstance.vm_status.in_(['running', 'starting', 'cloning'])
                ).all()
            }

            # Todas las VMs/CTs en Proxmox
            all_vms = proxmox("all", "list").get("items", [])

            # Huérfanas: tienen prefijo 'cr-', no son templates, no están en la BD
            for vm in all_vms:
                if (vm.get("name", "").startswith("cr-")
                    and vm["vmid"] not in active_vmids
                    and not vm.get("template")):
                    proxmox(vm.get("type", "lxc"), "destroy", vmid=vm["vmid"])

        finally:
            db.close()
