# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
#!/usr/bin/env python3
"""
AnÃ¡lisis profundo con radare2 via r2pipe.
Busca dispatch handlers, IOCTLs y cadenas de llamada peligrosas.
"""
import r2pipe
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

def analyze_ioctl_handler(driver_path: str) -> dict:
    """Encuentra y desensambla el handler de IRP_MJ_DEVICE_CONTROL."""
    r2 = r2pipe.open(driver_path, flags=["-2"])
    r2.cmd("e asm.syntax=intel")
    r2.cmd("aaa")  # AnÃ¡lisis completo

    report = {"file": Path(driver_path).name}

    # Buscar imports de IoCompleteRequest (indica handlers de IOCTL)
    imports = r2.cmdj("iij") or []
    io_complete = None
    for imp in imports:
        if "IoCompleteRequest" in imp.get("name", ""):
            io_complete = imp.get("plt", 0)
            break

    if not io_complete:
        r2.quit()
        return {"error": "No IoCompleteRequest â€” probablemente no WDM"}

    # Encontrar funciones que llaman a IoCompleteRequest
    xrefs = r2.cmdj(f"axtj {io_complete}") or []
    handlers = set()
    for xref in xrefs:
        handlers.add(xref.get("fcn_addr", 0))

    # Buscar cÃ³digos IOCTL en cada handler
    ioctl_codes = []
    for addr in handlers:
        disasm = r2.cmd(f"pdf @ {addr}")
        for line in disasm.split('\n'):
            # PatrÃ³n: cmp con constante que parece IOCTL
            if 'cmp' in line and '0x22' in line:
                # Extraer valor hexadecimal
                parts = line.split('0x')
                for part in parts[1:]:
                    hex_str = ""
                    for c in part:
                        if c in '0123456789abcdefABCDEF':
                            hex_str += c
                        else:
                            break
                    if len(hex_str) >= 5:
                        val = int(hex_str, 16)
                        method = val & 0x3
                        ioctl_codes.append({
                            "code": hex(val),
                            "method": method,
                            "method_name": {
                                0: "BUFFERED",
                                1: "IN_DIRECT",
                                2: "OUT_DIRECT",
                                3: "NEITHER"
                            }.get(method, "UNKNOWN"),
                        })

    report["ioctl_codes"] = ioctl_codes
    report["handler_count"] = len(handlers)

    r2.quit()
    return report
