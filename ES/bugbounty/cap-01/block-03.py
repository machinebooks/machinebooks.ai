# Extraído de: LibroBugBounty/cap-01-primera-vuln-agente.md
# Análisis de IOCTL con radare2 via r2pipe
# Ejecutado dentro del contenedor Docker
import r2pipe

r2 = r2pipe.open("/lab/drivers/AsIO3.sys", flags=["-2"])
r2.cmd("aaa")  # Análisis completo

# Buscar dispatch handler de IRP_MJ_DEVICE_CONTROL
functions = r2.cmdj("aflj") or []
for f in functions:
    disasm = r2.cmd(f"pdf @ {f['offset']}")
    # Buscar comparaciones con códigos IOCTL
    if "cmp" in disasm and "0x22" in disasm:
        for line in disasm.split('\n'):
            if 'cmp' in line and '0x22' in line:
                print(f"IOCTL candidate: {line.strip()}")

# Resultado: 16 IOCTLs identificados
# 4 con METHOD_NEITHER (0x3) — PUNTEROS SIN VALIDAR
# El más peligroso: código que llama a MmMapIoSpace
# con dirección física controlada por el usuario
