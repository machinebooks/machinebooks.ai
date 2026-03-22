# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: recursos separados por tipo
# Patrón: backend/services/proxmox_sdk_manager.py

async def get_all_resources_separated(self, cluster_id=None):
    """
    SIEMPRE separar VMs de Templates.
    El frontend recibe dos listas independientes con
    acciones permitidas explicitas.
    """
    vms = await self.get_vms(cluster_id)
    templates = await self.get_templates(cluster_id)

    return {
        'virtual_machines': {
            'data': vms,
            'available_actions': [
                'start', 'stop', 'restart', 'delete',
                'configure', 'console', 'snapshot'
            ],
            'type': 'manageable_vms'
        },
        'templates': {
            'data': templates,
            'available_actions': ['clone', 'delete', 'configure'],
            'type': 'cloneable_templates'
        },
        'separation_enforced': True
    }
