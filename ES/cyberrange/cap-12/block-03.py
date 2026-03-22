# Extraído de: LibroCyberrange/cap-12-sistema-ctf.md
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.models import Challenge, ChallengeInstance
from backend.services.proxmox_sdk_service import proxmox
from backend.services.dynamic_flag_service import DynamicFlagService


class ChallengeDeploymentService:
    """
    Flujo completo de despliegue:
    1. Clonar template LXC/QEMU → instancia del usuario
    2. Arrancar instancia y obtener IP
    3. Generar flag dinámica única
    4. Ejecutar playbook de setup (inyecta flag en la VM)
    5. Devolver IP + credenciales al usuario
    """

    @staticmethod
    def deploy_challenge_instance(
        db: Session,
        challenge: Challenge,
        user_id: int
    ) -> Dict[str, Any]:

        if not challenge.template_vmid:
            return {"success": False, "error": "Sin template configurado"}

        # Verificar instancia activa existente
        existing = db.query(ChallengeInstance).filter_by(
            challenge_id=challenge.id,
            user_id=user_id,
            state='open'
        ).first()

        if existing and existing.vmid and existing.vm_status == 'running':
            return {
                "success": True,
                "already_exists": True,
                "instance_id": existing.id,
                "ip_address": existing.ip_address,
                "message": "Instancia ya activa"
            }

        vm_type = challenge.template_type or 'lxc'
        vm_name = f"cr-u{user_id}-c{challenge.id}"

        # Crear registro de instancia
        instance = ChallengeInstance(
            challenge_id=challenge.id,
            user_id=user_id,
            state='open',
            started_at=datetime.utcnow(),
            vm_type=vm_type,
            vm_status='cloning'
        )
        db.add(instance)
        db.commit()

        # TTL: combinar configuración del challenge con tiempo límite
        ttl_hours = challenge.vm_ttl_hours or 2
        if challenge.time_limit_minutes:
            ttl_hours = max(ttl_hours, challenge.time_limit_minutes / 60)
        instance.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        db.commit()

        # 1. Clonar template (linked clone para velocidad)
        clone_result = proxmox(
            vm_type, "clone",
            template_vmid=challenge.template_vmid,
            name=vm_name,
            linked=True  # Linked clone: rápido y eficiente
        )

        if not clone_result.get("success"):
            instance.vm_status = 'error'
            db.commit()
            return {"success": False, "error": clone_result.get("error")}

        new_vmid = clone_result["new_vmid"]
        node = clone_result["node"]
        instance.vmid = new_vmid
        instance.vm_status = 'starting'
        db.commit()

        # 2. Arrancar instancia
        proxmox(vm_type, "start", vmid=new_vmid, node=node)

        # 3. Esperar asignación de IP (max 60 segundos)
        ip_address = None
        for _ in range(30):
            time.sleep(2)
            ip_result = proxmox(vm_type, "ip", vmid=new_vmid, node=node)
            if ip_result.get("success"):
                ip_address = ip_result["result"]
                break

        instance.ip_address = ip_address
        instance.vm_status = 'running'
        db.commit()

        # 4. Generar flag dinámica
        flag_value = None
        if challenge.flag_type == 'dynamic':
            flag_value = DynamicFlagService.generate_flag_for_instance(
                db, instance, force_new=True
            )

        # 5. Ejecutar playbook de setup (inyecta flag en la VM)
        if challenge.setup_playbook_yaml and ip_address:
            _run_setup_playbook(instance, challenge, ip_address, flag_value)

        return {
            "success": True,
            "instance_id": instance.id,
            "vmid": new_vmid,
            "ip_address": ip_address,
            "vm_type": vm_type,
            "expires_at": instance.expires_at.isoformat(),
        }
