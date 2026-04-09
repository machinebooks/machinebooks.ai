# Extraido de: LibroAISafety/cap-14-infraestructura.md
# Script didáctico de reconocimiento de superficie de ataque
# para una aplicación de IA de escritorio en Windows
# NOTA: Este código es educativo, no una herramienta de ataque

import subprocess
import json
from dataclasses import dataclass

@dataclass
class ProcessInfo:
    pid: int
    name: str
    user: str
    listening_ports: list[int]
    loaded_dlls: list[str]
    writable_paths: list[str]

def recon_surface(app_name: str) -> dict:
    """
    Recopila información sobre la superficie de ataque
    de una aplicación en ejecución.
    Requiere ejecutarse con permisos de administrador.
    """
    surface = {
        "procesos": [],
        "puertos_locales": [],
        "ficheros_asar": [],
        "dlls_sin_firma": [],
        "servicios_persistentes": [],
    }

    # 1. Listar procesos de la aplicación
    # (simplificado — en producción usar WMI o psutil)
    # surface["procesos"] = get_processes_by_name(app_name)

    # 2. Verificar puertos en escucha
    # surface["puertos_locales"] = get_listening_ports(app_name)

    # 3. Buscar ficheros ASAR sin protección
    # surface["ficheros_asar"] = find_unprotected_asar(app_name)

    # 4. Identificar DLLs cargadas sin firma válida
    # surface["dlls_sin_firma"] = find_unsigned_dlls(app_name)

    # 5. Detectar servicios que persisten tras cerrar la app
    # surface["servicios_persistentes"] = find_persistent_services(app_name)

    return surface
