# Extraído de: LibroCyberrange/cap-01-que-es-cyber-range.md
# Modelo de template de VM para el catálogo del Cyber Range
# Ejemplo didáctico: patrones/templates/models.py

from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum
from sqlalchemy.orm import relationship

class VMTemplate(Base):
    __tablename__ = "vm_template"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    proxmox_vmid = Column(Integer, unique=True)      # ID en Proxmox
    os_type = Column(Enum("windows", "linux", "pfsense", "other"))
    os_version = Column(String(50))                    # Ej: "Windows Server 2022"

    # Clasificación para búsqueda y generación de escenarios
    category = Column(Enum(
        "attacker",          # Kali, Parrot, herramientas ofensivas
        "target_server",     # Servidores vulnerables por diseño
        "target_workstation",# Estaciones de trabajo de usuario
        "infrastructure",    # AD, DNS, DHCP, SIEM, firewalls
        "ot_device",         # Simuladores de dispositivos industriales
        "custom"             # Templates personalizados por organizador
    ))

    # Recursos necesarios (para cálculo de capacidad)
    min_cpu = Column(Integer, default=2)
    min_memory_mb = Column(Integer, default=2048)
    min_disk_gb = Column(Integer, default=20)

    # Metadatos para generación de escenarios con IA
    description = Column(String(500))     # Descripción técnica para Claude
    services = Column(JSON)               # Ej: ["ssh", "http", "smb"]
    vulnerabilities = Column(JSON)        # Ej: ["kerberoasting", "asreproast"]
    mitre_techniques = Column(JSON)       # Ej: ["T1558.003", "T1558.004"]

    # Estado y disponibilidad
    is_active = Column(Boolean, default=True)
    clone_count = Column(Integer, default=0)  # Uso acumulado
