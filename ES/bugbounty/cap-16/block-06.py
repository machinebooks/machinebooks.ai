# Extraído de: LibroBugBounty/cap-16-reconocimiento-surface.md
import subprocess
import re

def audit_services(service_names=None):
    """Audita DACL y configuración de servicios."""
    findings = []

    # Si no se especifican nombres, buscar servicios del vendor
    if service_names is None:
        result = subprocess.run(
            ["sc", "query", "type=", "service", "state=", "all"],
            capture_output=True, text=True
        )
        # Filtrar por nombre del vendor
        service_names = re.findall(
            r'SERVICE_NAME:\s+(\S+)',
            result.stdout
        )

    for svc_name in service_names:
        svc = {"name": svc_name, "issues": []}

        # Configuración del servicio
        qc = subprocess.run(
            ["sc", "qc", svc_name], capture_output=True, text=True
        )
        if "LocalSystem" in qc.stdout:
            svc["account"] = "SYSTEM"
            svc["issues"].append("Runs as SYSTEM")

        # Extraer path del binario
        path_match = re.search(
            r'BINARY_PATH_NAME\s+:\s+(.+)', qc.stdout
        )
        if path_match:
            svc["binary_path"] = path_match.group(1).strip()

        # DACL del servicio
        sd = subprocess.run(
            ["sc", "sdshow", svc_name], capture_output=True, text=True
        )
        dacl = sd.stdout.strip()
        svc["dacl"] = dacl

        # Buscar permisos peligrosos en DACL
        # BU = BUILTIN\Users, WD = Everyone
        # RP = SERVICE_START, WP = SERVICE_STOP
        if "(A;;RPWP" in dacl and "BU)" in dacl:
            svc["issues"].append("Users can START/STOP")
        if "(A;;RPWP" in dacl and "WD)" in dacl:
            svc["issues"].append("Everyone can START/STOP")
        if "DC" in dacl:
            svc["issues"].append("Users can change config")

        if svc["issues"]:
            findings.append(svc)

    return findings
