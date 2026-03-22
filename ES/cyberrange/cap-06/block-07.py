# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_manager.py
# Creación de clones vinculados para un ejercicio

async def create_linked_clone(
    self,
    template_id: int,
    base_name: str,
    count: int = 1,
    network: str = None,
    workzone: Workzone = None
) -> Dict[str, Any]:
    """
    Crear clones vinculados desde un template para un ejercicio.
    Cada clon se etiqueta con su workzone y se conecta a la red.
    """
    template = self.db.query(ProxmoxTemplate).get(template_id)
    node = self.db.query(ProxmoxNode).get(template.node_id)
    sdk = self._get_live_sdk()

    created_vms = []
    start_vmid = self._get_next_available_vmid(template.cluster_id)

    for i in range(count):
        current_vmid = start_vmid + i
        vm_name = f"{base_name}-{i+1}" if count > 1 else base_name

        # Normalizar nombre a hostname DNS válido
        normalized_name = self.normalize_vm_name_to_hostname(vm_name)

        # 1. Clonar template (linked clone)
        success = await sdk.create_vm_from_template(
            node=node.name,
            template_vmid=template.vmid,
            new_vmid=current_vmid,
            name=normalized_name,
            full=0  # Linked clone
        )

        if not success:
            continue

        # 2. Etiquetar con workzone
        tags = (template.tags or "").split(";")
        tags.append(f"wz_{workzone.id}")
        await sdk.update_vm_config(
            node.name, current_vmid,
            {"tags": ";".join(tags)}
        )

        # 3. Conectar a la red del ejercicio
        await sdk.connect_vm_to_vnetwork(
            node=node.name,
            vmid=current_vmid,
            network_name=network
        )

        # 4. Arrancar la VM
        await sdk.start_vm(node=node.name, vmid=current_vmid)

        # 5. Registrar en MySQL (mirror de Proxmox)
        new_vm = ProxmoxVM(
            cluster_id=template.cluster_id,
            node_id=template.node_id,
            vmid=current_vmid,
            name=normalized_name,
            status='running',
            cpu_cores=template.cpu_cores,
            memory_mb=template.memory_mb,
            template_id=template.id,
            workzone_id=workzone.id,
            created_at=datetime.now()
        )
        self.db.add(new_vm)
        created_vms.append({"vmid": current_vmid, "name": vm_name})

    self.db.commit()
    return {"created": len(created_vms), "vms": created_vms}
