# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
import r2pipe
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

cs = Cs(CS_ARCH_X86, CS_MODE_64)
cs.detail = True

# Offsets de IRP en DRIVER_OBJECT (x64)
IRP_OFFSETS = {
    0x70:  "IRP_MJ_CREATE",         # Open handle
    0x80:  "IRP_MJ_CLOSE",          # Close handle
    0xE0:  "IRP_MJ_DEVICE_CONTROL", # IOCTLs — superficie de ataque principal
    0xE8:  "IRP_MJ_INTERNAL_DEVICE_CONTROL",
    0x100: "IRP_MJ_CLEANUP",
}

def find_dispatch_table(r2, entry_addr):
    """Busca dónde DriverEntry configura la tabla MajorFunction."""
    raw_bytes = bytes(r2.cmdj(f"pxj 512 @ {entry_addr}"))
    handlers = {}

    for insn in cs.disasm(raw_bytes, entry_addr):
        # Patrón: mov qword [rcx + offset], valor
        # RCX = PDRIVER_OBJECT, offset = IRP type
        if insn.mnemonic == 'mov' and '+' in insn.op_str:
            if ']' in insn.op_str:
                parts = insn.op_str.split('+')
                if len(parts) >= 2:
                    offset_str = parts[-1].strip().rstrip(']')
                    offset_str = offset_str.split(',')[0].strip()
                    try:
                        offset = int(offset_str, 16)
                        if offset in IRP_OFFSETS:
                            handlers[offset] = {
                                "irp_type": IRP_OFFSETS[offset],
                                "instruction": f"{insn.mnemonic} {insn.op_str}",
                                "address": hex(insn.address),
                            }
                    except ValueError:
                        pass

    return handlers
