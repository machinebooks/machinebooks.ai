# Extraído de: LibroCyberrange/cap-13-escenarios-topologias.md
# backend/services/scenario_deployment.py
import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models import (
    ScenarioDeployment, ScenarioInstance,
    ScenarioTemplate, Workzone
)
from backend.services.proxmox_sdk_manager import get_proxmox_sdk_manager
from backend.services.ansible_executor import AnsibleExecutor
from backend.services.websocket_manager import ws_manager
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class ScenarioDeploymentService:
    """Orquesta el despliegue completo de un escenario:
    validación → redes → clonación → conectividad → playbooks → verificación → publicación."""

    def __init__(self):
        self.proxmox = None
        self.ansible = AnsibleExecutor()

    def _get_proxmox(self):
        """Acceso lazy al SDK de Proxmox."""
        if not self.proxmox:
            self.proxmox = get_proxmox_sdk_manager()
        return self.proxmox

    async def deploy_scenario(
        self,
        deployment_id: int,
        template: ScenarioTemplate,
        workzone: Workzone,
        custom_config: Optional[Dict] = None,
        db: Session = None
    ) -> bool:
        """Pipeline completo de despliegue en 7 pasos."""

        deployment = db.query(ScenarioDeployment).get(deployment_id)
        if not deployment:
            return False

        # Combinar configuración base con personalizaciones
        config = {
            "topology": template.topology_config,
            "vms": template.vm_configs,
            "networks": template.network_configs,
            "security": template.security_configs or {}
        }
        if custom_config:
            config = self._merge_configs(config, custom_config)

        try:
            # Paso 1: Validar recursos disponibles
            await self._update_progress(deployment, 5, "Validando recursos", db)
            await self._validate_resources(config, workzone)

            # Paso 2: Crear redes y VLANs
            await self._update_progress(deployment, 15, "Creando redes", db)
            network_map = await self._deploy_networks(
                deployment, config, workzone, db
            )

            # Paso 3: Clonar VMs desde templates (linked clones)
            await self._update_progress(deployment, 35, "Clonando VMs", db)
            vm_map = await self._clone_vms(
                deployment, config, workzone, network_map, db
            )

            # Paso 4: Configurar conectividad (IPs, interfaces, DNS)
            await self._update_progress(deployment, 50, "Configurando red", db)
            await self._configure_connectivity(vm_map, network_map, config, db)

            # Paso 5: Ejecutar playbooks de Ansible
            await self._update_progress(deployment, 65, "Ejecutando playbooks", db)
            await self._execute_playbooks(
                deployment, config, vm_map, db
            )

            # Paso 6: Verificar despliegue (health checks)
            await self._update_progress(deployment, 85, "Verificando despliegue", db)
            await self._verify_deployment(deployment, vm_map, db)

            # Paso 7: Publicar topología al canvas
            await self._update_progress(deployment, 95, "Publicando topología", db)
            await self._publish_topology(deployment, vm_map, network_map, db)

            # Completado
            deployment.status = "deployed"
            deployment.progress = 100
            deployment.deploy_completed_at = datetime.utcnow()
            db.commit()

            await ws_manager.emit_to_workzone(
                workzone.id,
                "deployment_complete",
                {"deployment_id": deployment.id, "status": "deployed"}
            )
            return True

        except Exception as e:
            logger.error(f"Deployment {deployment_id} failed: {e}")
            deployment.status = "error"
            deployment.error_message = str(e)
            db.commit()

            await ws_manager.emit_to_workzone(
                workzone.id,
                "deployment_error",
                {"deployment_id": deployment.id, "error": str(e)}
            )
            return False

    async def _validate_resources(self, config: Dict, workzone: Workzone):
        """Paso 1: Verificar que Proxmox tiene recursos suficientes
        para desplegar todas las VMs del escenario."""
        proxmox = self._get_proxmox()
        node_status = await proxmox.get_node_status(workzone.proxmox_node)

        total_cpu = sum(
            vm.get("cpu", 1) for vm in config["vms"].values()
        )
        total_memory = sum(
            vm.get("memory_mb", 1024) for vm in config["vms"].values()
        )
        total_disk = sum(
            vm.get("disk_gb", 20) for vm in config["vms"].values()
        )

        available_cpu = node_status["maxcpu"] - node_status["cpu_used"]
        available_memory = node_status["maxmem_mb"] - node_status["mem_used_mb"]
        available_disk = node_status["storage_free_gb"]

        if total_cpu > available_cpu:
            raise ValueError(
                f"CPU insuficiente: necesita {total_cpu} cores, "
                f"disponibles {available_cpu}"
            )
        if total_memory > available_memory:
            raise ValueError(
                f"Memoria insuficiente: necesita {total_memory}MB, "
                f"disponible {available_memory}MB"
            )
        if total_disk > available_disk:
            raise ValueError(
                f"Disco insuficiente: necesita {total_disk}GB, "
                f"disponible {available_disk}GB"
            )

        logger.info(
            f"Validación OK: {total_cpu} CPU, {total_memory}MB RAM, "
            f"{total_disk}GB disco"
        )

    async def _deploy_networks(
        self, deployment, config, workzone, db
    ) -> Dict[str, Any]:
        """Paso 2: Crear VLANs y bridges en Proxmox."""
        proxmox = self._get_proxmox()
        network_map = {}

        for net_name, net_config in config["networks"].items():
            vlan_id = net_config.get("vlan_id")
            cidr = net_config["cidr"]
            gateway = net_config.get("gateway")

            # Crear bridge con VLAN tag en Proxmox
            bridge = await proxmox.create_network_bridge(
                node=workzone.proxmox_node,
                vlan_id=vlan_id,
                cidr=cidr,
                gateway=gateway,
                comment=f"Scenario {deployment.id}: {net_name}"
            )

            # Registrar instancia de red
            instance = ScenarioInstance(
                deployment_id=deployment.id,
                instance_type="network",
                name=net_name,
                proxmox_id=bridge["bridge_name"],
                config={"cidr": cidr, "vlan_id": vlan_id, "gateway": gateway},
                status="running"
            )
            db.add(instance)
            network_map[net_name] = {
                "bridge": bridge["bridge_name"],
                "cidr": cidr,
                "gateway": gateway,
                "vlan_id": vlan_id
            }

        db.commit()
        return network_map

    async def _clone_vms(
        self, deployment, config, workzone, network_map, db
    ) -> Dict[str, Any]:
        """Paso 3: Clonar VMs usando linked clones de Proxmox."""
        proxmox = self._get_proxmox()
        vm_map = {}

        for vm_name, vm_config in config["vms"].items():
            template_id = vm_config["template_vmid"]
            target_network = vm_config.get("network", "default")
            bridge = network_map.get(target_network, {}).get("bridge", "vmbr0")

            # Linked clone: rápido y ligero
            new_vmid = await proxmox.clone_vm(
                node=workzone.proxmox_node,
                source_vmid=template_id,
                new_name=f"{deployment.id}-{vm_name}",
                full_clone=False,       # Linked clone
                target_storage="local-lvm",
                description=f"Escenario {deployment.id} - {vm_name}"
            )

            # Configurar recursos
            await proxmox.update_vm_config(
                node=workzone.proxmox_node,
                vmid=new_vmid,
                cpu=vm_config.get("cpu", 1),
                memory=vm_config.get("memory_mb", 1024),
                net0=f"virtio,bridge={bridge}"
            )

            # Registrar instancia de VM
            instance = ScenarioInstance(
                deployment_id=deployment.id,
                instance_type="vm",
                name=vm_name,
                proxmox_id=str(new_vmid),
                config=vm_config,
                status="creating",
                ip_address=vm_config.get("ip")
            )
            db.add(instance)
            vm_map[vm_name] = {
                "vmid": new_vmid,
                "ip": vm_config.get("ip"),
                "os": vm_config.get("os"),
                "bridge": bridge
            }

            # Notificar progreso por cada VM
            await ws_manager.emit_to_workzone(
                workzone.id,
                "vm_cloned",
                {"vm_name": vm_name, "vmid": new_vmid}
            )

        db.commit()

        # Arrancar todas las VMs en paralelo
        start_tasks = [
            proxmox.start_vm(workzone.proxmox_node, vm["vmid"])
            for vm in vm_map.values()
        ]
        await asyncio.gather(*start_tasks)

        return vm_map

    async def _configure_connectivity(
        self, vm_map, network_map, config, db
    ):
        """Paso 4: Asignar IPs estáticas y configurar DNS."""
        proxmox = self._get_proxmox()

        for vm_name, vm_info in vm_map.items():
            vm_config = config["vms"].get(vm_name, {})
            ip = vm_config.get("ip")
            gateway = None
            network_name = vm_config.get("network")

            if network_name and network_name in network_map:
                gateway = network_map[network_name].get("gateway")

            if ip:
                # Configurar IP estática vía Cloud-Init o guest agent
                await proxmox.set_vm_ip(
                    node=config.get("proxmox_node", "pve"),
                    vmid=vm_info["vmid"],
                    ip=ip,
                    gateway=gateway
                )

    async def _execute_playbooks(
        self, deployment, config, vm_map, db
    ):
        """Paso 5: Ejecutar playbooks de Ansible para instalar servicios,
        inyectar vulnerabilidades y plantar flags."""

        # Generar inventario dinámico desde las VMs desplegadas
        inventory = self._build_ansible_inventory(vm_map, config)

        # Obtener lista de playbooks del escenario
        playbooks = config.get("security", {}).get("playbooks", [])

        for playbook_path in playbooks:
            logger.info(f"Ejecutando playbook: {playbook_path}")

            # ansible-runner ejecuta el playbook con streaming de eventos
            result = await self.ansible.run_playbook(
                playbook=playbook_path,
                inventory=inventory,
                extra_vars={
                    "deployment_id": deployment.id,
                    "scenario_name": deployment.scenario_template_id
                },
                event_handler=lambda event: self._stream_ansible_event(
                    deployment, event
                )
            )

            if result.status != "successful":
                raise RuntimeError(
                    f"Playbook {playbook_path} falló: {result.stderr}"
                )

        # Plantar flags si están definidos en security_configs
        flags = config.get("security", {}).get("flags", [])
        if flags:
            await self._plant_flags(flags, vm_map, inventory)

    def _build_ansible_inventory(
        self, vm_map: Dict, config: Dict
    ) -> Dict:
        """Construir inventario dinámico de Ansible agrupado por rol."""
        inventory = {"all": {"hosts": {}, "children": {}}}
        groups = {}

        for vm_name, vm_info in vm_map.items():
            vm_config = config["vms"].get(vm_name, {})
            ansible_groups = vm_config.get("ansible_groups", ["ungrouped"])
            host_vars = {
                "ansible_host": vm_info["ip"],
                "ansible_user": vm_config.get("ansible_user", "root"),
            }

            # SSH para Linux, WinRM para Windows
            if "windows" in vm_info.get("os", "").lower():
                host_vars["ansible_connection"] = "winrm"
                host_vars["ansible_winrm_transport"] = "ntlm"
                host_vars["ansible_port"] = 5986
            else:
                host_vars["ansible_connection"] = "ssh"
                host_vars["ansible_port"] = 22

            inventory["all"]["hosts"][vm_name] = host_vars

            for group in ansible_groups:
                if group not in groups:
                    groups[group] = {"hosts": {}}
                groups[group]["hosts"][vm_name] = {}

        inventory["all"]["children"] = groups
        return inventory

    async def _plant_flags(
        self, flags: List[Dict], vm_map: Dict, inventory: Dict
    ):
        """Plantar flags en las VMs indicadas. Cada flag tiene un hash
        único que se verifica cuando el participante lo envía."""
        for flag in flags:
            target_vm = flag["target_vm"]
            flag_value = flag["value"]
            flag_path = flag.get("path", "/root/flag.txt")
            flag_hash = hashlib.sha256(flag_value.encode()).hexdigest()

            if target_vm in vm_map:
                # Ejecutar comando remoto para plantar el flag
                await self.ansible.run_adhoc(
                    host=vm_map[target_vm]["ip"],
                    module="copy",
                    args=f'content="{flag_value}" dest="{flag_path}" mode=0400',
                    inventory=inventory
                )
                logger.info(
                    f"Flag plantado en {target_vm}:{flag_path} "
                    f"(hash: {flag_hash[:12]}...)"
                )

    async def _verify_deployment(self, deployment, vm_map, db):
        """Paso 6: Health checks en cada VM desplegada."""
        proxmox = self._get_proxmox()

        for vm_name, vm_info in vm_map.items():
            # Verificar que la VM está corriendo
            status = await proxmox.get_vm_status(
                node="pve", vmid=vm_info["vmid"]
            )
            if status.get("status") != "running":
                logger.warning(f"VM {vm_name} no está corriendo: {status}")

            # Verificar conectividad de red (ping desde el host)
            if vm_info.get("ip"):
                reachable = await proxmox.ping_vm(vm_info["ip"], timeout=30)
                if not reachable:
                    logger.warning(
                        f"VM {vm_name} ({vm_info['ip']}) no responde a ping"
                    )

            # Actualizar estado de la instancia
            instance = db.query(ScenarioInstance).filter(
                ScenarioInstance.deployment_id == deployment.id,
                ScenarioInstance.name == vm_name
            ).first()
            if instance:
                instance.status = "running" if status.get("status") == "running" else "error"
                db.commit()

    async def _publish_topology(
        self, deployment, vm_map, network_map, db
    ):
        """Paso 7: Emitir la topología completa al canvas vía WebSocket."""
        canvas_nodes = []
        canvas_edges = []

        # Nodos de red (como contenedores visuales)
        y_offset = 50
        for net_name, net_info in network_map.items():
            canvas_nodes.append({
                "id": f"net-{net_name}",
                "name": net_name,
                "type": "network",
                "is_container": True,
                "network_cidr": net_info["cidr"],
                "bridge": net_info["bridge"],
                "vlan_id": net_info["vlan_id"],
                "x": 100,
                "y": y_offset,
                "size": {"width": 600, "height": 200}
            })
            y_offset += 250

        # Nodos de VM (posicionados dentro de su red contenedora)
        for vm_name, vm_info in vm_map.items():
            canvas_nodes.append({
                "id": f"vm-{vm_info['vmid']}",
                "name": vm_name,
                "type": "vm",
                "vmid": vm_info["vmid"],
                "ip_address": vm_info.get("ip"),
                "os_type": vm_info.get("os"),
                "status": "connected",
                "power_state": "poweredOn",
                "deployed": True,
                "scenario_id": deployment.scenario_template_id,
                "x": 150,
                "y": 100
            })

        await ws_manager.emit_to_workzone(
            deployment.workzone_id,
            "topology_update",
            {
                "deployment_id": deployment.id,
                "nodes": canvas_nodes,
                "edges": canvas_edges
            }
        )

    async def _update_progress(
        self, deployment, progress, message, db
    ):
        """Actualizar progreso en BD y notificar vía WebSocket."""
        deployment.progress = progress
        db.commit()

        await ws_manager.emit_to_workzone(
            deployment.workzone_id,
            "deployment_progress",
            {
                "deployment_id": deployment.id,
                "progress": progress,
                "message": message
            }
        )

    async def _stream_ansible_event(self, deployment, event):
        """Retransmitir eventos de ansible-runner al frontend."""
        await ws_manager.emit_to_workzone(
            deployment.workzone_id,
            "ansible_event",
            {
                "deployment_id": deployment.id,
                "event_type": event.get("event"),
                "task": event.get("event_data", {}).get("task"),
                "host": event.get("event_data", {}).get("host"),
                "status": event.get("event_data", {}).get("res", {}).get("changed")
            }
        )

    def _merge_configs(self, base: Dict, custom: Dict) -> Dict:
        """Merge recursivo de configuración personalizada sobre la base."""
        result = base.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result


# Instancia global del servicio
scenario_deployment_service = ScenarioDeploymentService()
