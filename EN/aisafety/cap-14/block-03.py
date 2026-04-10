# Extracted from: LibroAISafety/ch-14-infrastructure.md
# Didactic attack surface reconnaissance script
# for an AI desktop application on Windows
# NOTE: This code is educational, not an attack tool

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
    Collects information about the attack surface
    of a running application.
    Requires administrator permissions to run.
    """
    surface = {
        "processes": [],
        "local_ports": [],
        "asar_files": [],
        "unsigned_dlls": [],
        "persistent_services": [],
    }

    # 1. List application processes
    # (simplified — in production use WMI or psutil)
    # surface["processes"] = get_processes_by_name(app_name)

    # 2. Check listening ports
    # surface["local_ports"] = get_listening_ports(app_name)

    # 3. Find unprotected ASAR files
    # surface["asar_files"] = find_unprotected_asar(app_name)

    # 4. Identify loaded DLLs without valid signature
    # surface["unsigned_dlls"] = find_unsigned_dlls(app_name)

    # 5. Detect services persisting after closing the app
    # surface["persistent_services"] = find_persistent_services(app_name)

    return surface
