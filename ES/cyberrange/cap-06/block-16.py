# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Capa de compatibilidad: métodos async que delegan en proxmox()

class ProxmoxSDKService:
    """
    Wrapper async sobre la función unificada proxmox().
    Los callers existentes siguen funcionando sin cambios.
    """

    async def create_vm_from_template(
        self, node, template_vmid, new_vmid, name, **kwargs
    ) -> bool:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: proxmox(
                "auto", "clone",
                template_vmid=template_vmid,
                name=name,
                new_vmid=new_vmid,
                node=node,
                **kwargs
            )
        )
        return result.get("success", False)
