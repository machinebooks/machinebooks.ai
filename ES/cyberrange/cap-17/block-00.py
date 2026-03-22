# Extraído de: LibroCyberrange/cap-17-generacion-escenarios-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/scenario_agent.py
import anthropic
from agents import Agent, Runner, function_tool
from typing import Optional
from backend.services.proxmox_sdk_manager import get_proxmox_sdk_manager
from backend.models import VMTemplate, Workzone, ScenarioTemplate
from backend.database import get_db

# --- Herramientas del agente ---

@function_tool
def list_vm_templates(os_type: Optional[str] = None) -> list:
    """
    Lista los templates de VM disponibles en Proxmox.
    Cada template incluye: nombre, SO, CPU, RAM, disco y tags.
    El agente usa esta información para seleccionar las VMs del escenario.
    """
    db = next(get_db())
    query = db.query(VMTemplate).filter(VMTemplate.is_public == True)
    if os_type:
        query = query.filter(VMTemplate.guest_os.ilike(f"%{os_type}%"))

    templates = query.all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "guest_os": t.guest_os,
            "cpu": t.cpu,
            "ram_mb": t.ram_mb,
            "disk_gb": t.disk_gb,
            "tags": t.tags or []
        }
        for t in templates
    ]

@function_tool
def validate_network_config(cidr: str, vlan_id: int) -> dict:
    """
    Valida que un rango de red CIDR y VLAN no colisionan
    con workzones activas. Devuelve si es válido y motivo.
    """
    import ipaddress
    db = next(get_db())

    # Validar formato CIDR
    try:
        requested_net = ipaddress.ip_network(cidr, strict=False)
    except ValueError as e:
        return {"valid": False, "reason": f"CIDR inválido: {str(e)}"}

    # Verificar colisión de VLAN
    existing_vlan = db.query(Workzone).filter(
        Workzone.vlan_id == vlan_id,
        Workzone.status == "active"
    ).first()
    if existing_vlan:
        return {"valid": False, "reason": f"VLAN {vlan_id} ya en uso"}

    # Verificar solapamiento de rangos IP
    active_zones = db.query(Workzone).filter(
        Workzone.network_cidr.isnot(None),
        Workzone.status == "active"
    ).all()

    for zone in active_zones:
        existing_net = ipaddress.ip_network(zone.network_cidr, strict=False)
        if requested_net.overlaps(existing_net):
            return {
                "valid": False,
                "reason": f"CIDR {cidr} solapa con {zone.name}"
            }

    return {"valid": True, "reason": "Configuración de red disponible"}

@function_tool
def check_resource_availability(
    workzone_id: int, cpu_needed: int, memory_mb: int, storage_gb: int
) -> dict:
    """
    Verifica si una workzone tiene recursos suficientes para
    desplegar las VMs del escenario. Compara contra límites
    configurados y uso actual.
    """
    db = next(get_db())
    wz = db.query(Workzone).filter(Workzone.id == workzone_id).first()

    if not wz:
        return {"available": False, "reason": "Workzone no encontrada"}

    # Calcular uso actual de la workzone
    from sqlalchemy import func
    from backend.models import WorkzoneInstance
    current_usage = db.query(
        func.sum(WorkzoneInstance.config["cpu"].as_integer()),
        func.sum(WorkzoneInstance.config["ram_mb"].as_integer()),
    ).filter(
        WorkzoneInstance.workzone_id == workzone_id,
        WorkzoneInstance.status.in_(["running", "creating"])
    ).first()

    used_cpu = current_usage[0] or 0
    used_mem = current_usage[1] or 0

    available_cpu = (wz.cpu_limit or 32) - used_cpu
    available_mem = (wz.memory_limit or 65536) - used_mem
    available_storage = wz.storage_limit or 500

    if cpu_needed > available_cpu:
        return {"available": False, "reason": f"CPU insuficiente: necesitas {cpu_needed}, disponibles {available_cpu}"}
    if memory_mb > available_mem:
        return {"available": False, "reason": f"RAM insuficiente: necesitas {memory_mb}MB, disponibles {available_mem}MB"}
    if storage_gb > available_storage:
        return {"available": False, "reason": f"Disco insuficiente: necesitas {storage_gb}GB, disponibles {available_storage}GB"}

    return {
        "available": True,
        "remaining_cpu": available_cpu - cpu_needed,
        "remaining_memory_mb": available_mem - memory_mb,
        "remaining_storage_gb": available_storage - storage_gb
    }

@function_tool
def list_available_playbooks(category: Optional[str] = None) -> list:
    """
    Lista los playbooks de Ansible disponibles para configuración
    de vulnerabilidades. Cada playbook tiene nombre, categoría
    y descripción de lo que configura.
    """
    import os
    playbook_dir = "/opt/cyber-range/playbooks"
    categories = {
        "windows": "windows_playbooks",
        "kali": "kali",
        "cve": "cve_playbooks",
        "linux": "linux_service_playbooks",
        "iot": "iot_scenarios",
        "ot": "ot_scenarios",
        "scan": "scan_playbooks_unique",
    }

    results = []
    dirs_to_scan = (
        [categories[category]] if category and category in categories
        else categories.values()
    )

    for subdir in dirs_to_scan:
        full_path = os.path.join(playbook_dir, subdir)
        if not os.path.isdir(full_path):
            continue
        for fname in os.listdir(full_path):
            if fname.endswith((".yml", ".yaml")):
                results.append({
                    "name": fname,
                    "category": subdir,
                    "path": f"{subdir}/{fname}"
                })

    return results
