# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
import yara

# Reglas YARA para clasificar drivers por riesgo
DRIVER_RULES = """
rule HighRisk_PhysicalMemory {
    meta:
        description = "Driver with physical memory access"
        risk = "HIGH"
    strings:
        $mmap = "MmMapIoSpace" wide ascii
        $phys = "PhysicalMemory" wide
        $no_priv = "SePrivilegeCheck"
    condition:
        $mmap and $phys and not $no_priv
}

rule MediumRisk_IOPorts {
    meta:
        description = "Driver with I/O port access"
        risk = "MEDIUM"
    strings:
        $read = "READ_PORT_UCHAR" wide ascii
        $write = "WRITE_PORT_UCHAR" wide ascii
    condition:
        $read or $write
}

rule Info_DeviceName {
    meta:
        description = "Driver with accessible device"
    strings:
        $dev = "\\\\Device\\\\" wide
        $dos = "\\\\DosDevices\\\\" wide
    condition:
        $dev and $dos
}
"""

def classify_driver_yara(driver_path):
    """Clasifica un driver con YARA rules."""
    rules = yara.compile(source=DRIVER_RULES)
    matches = rules.match(str(driver_path))
    return [{"rule": m.rule, "meta": m.meta} for m in matches]
